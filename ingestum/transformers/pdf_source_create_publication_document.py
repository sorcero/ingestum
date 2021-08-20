# -*- coding: utf-8 -*-

#
# Copyright (c) 2021 Sorcero, Inc.
#
# This file is part of Sorcero's Language Intelligence platform
# (see https://www.sorcero.com).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#


import os
import tempfile
import cv2
from pytesseract.pytesseract import image_to_data, Output

from .. import sources
from .. import documents
from .. import transformers
from .base import BaseTransformer
from ingestum import utils

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from PyPDF2 import PdfFileReader
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from difflib import SequenceMatcher
from pdf2image import convert_from_path


__script__ = os.path.basename(__file__).replace(".py", "")


class BaseTitleParser:
    priority: int

    def get_title(self, source):
        raise NotImplementedError


class MetadataTitleParser(BaseTitleParser):
    """
    Extracts the title from the metadata (if any).
    """

    priority = 1

    def get_title(self, source):
        pdf = PdfFileReader(open(source.path, "rb"))
        info = pdf.getDocumentInfo()

        if info.title not in (None, ""):
            return utils.sanitize_string(info.title)
        return None


class PDFMinerTitleParser(BaseTitleParser):
    """
    Searches within the first page of the PDF and returns the
    title, which is defined as the phrase with the largest
    font, with a length between 5 and 20 words.
    """

    priority = 2

    def get_title(self, source):
        candidate = {"text": "", "height": 0}
        previous_candidate = {"text": "", "height": 0}

        for page_layout in extract_pages(source.path, maxpages=1):
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    for text_line in element:
                        line_height = text_line.y1 - text_line.y0

                        if line_height == candidate["height"]:
                            continuation = text_line.get_text().replace("\n", "")
                            candidate["text"] += f" {continuation}"
                        else:
                            word_count = len(candidate["text"].split())

                            if (
                                word_count > 5
                                and word_count < 20
                                and candidate["height"] > previous_candidate["height"]
                            ):
                                previous_candidate = candidate.copy()

                            candidate["height"] = line_height
                            candidate["text"] = text_line.get_text().replace("\n", "")

        word_count = len(candidate["text"].split())
        if (
            word_count > 5
            and word_count < 20
            and candidate["height"] > previous_candidate["height"]
        ):
            return utils.sanitize_string("".join(candidate["text"].splitlines()))
        elif previous_candidate["text"] != 0:
            return utils.sanitize_string(
                "".join(previous_candidate["text"].splitlines())
            )
        return None


class OCRTitleParser(BaseTitleParser):
    """
    Reconstructs the phrases in the text (adjacent lines belonging to the same element of text),
    and returns the title, which is defined as the phrase with the largest
    font, with a length between 5 and 20 words.
    """

    priority = 3

    def get_title(self, source):
        directory = tempfile.TemporaryDirectory()

        image_path = convert_from_path(
            pdf_path=source.path,
            output_folder=directory.name,
            first_page=1,
            last_page=1,
            paths_only=True,
        )[0]
        image = cv2.imread(image_path)

        directory.cleanup()

        image_data = image_to_data(image, output_type=Output.DICT)

        total_elements_num = len(image_data["level"])
        elements_by_block = {}
        for i in range(total_elements_num):
            block_num = image_data["block_num"][i]

            if block_num not in elements_by_block:
                elements_by_block[block_num] = []
            elements_by_block[block_num].append(i)

        # We get the following data from each line:
        # - Text
        # - Top (distance from the top of the page to the line's topmost point)
        # - Bottom (distance from the top of the page to the line's bottommost point)
        # - Separation (distance from the topmost point of the line to the bottommost point of the line above)
        info_per_line = []
        for block_num in elements_by_block.keys():
            line_num = -1
            top = image_data["top"][-1] + 1
            bottom = -1
            text = ""
            word_num_visited = set()

            for inner, outer in enumerate(elements_by_block[block_num]):
                if (
                    image_data["conf"][outer] == "-1"
                    or image_data["text"][outer].isspace()
                ):
                    continue
                current_line_num = image_data["line_num"][outer]

                if line_num == -1 or (
                    line_num == current_line_num
                    and image_data["word_num"][outer] not in word_num_visited
                ):
                    line_num = current_line_num
                    text += f" {image_data['text'][outer]}"
                    top = min(top, image_data["top"][outer])
                    bottom = max(
                        bottom, image_data["top"][outer] + image_data["height"][outer]
                    )
                    word_num_visited.add(image_data["word_num"][outer])

                    if inner == len(elements_by_block[block_num]) - 1:
                        info_per_line.append(
                            {
                                "text": text,
                                "top": top,
                                "bottom": bottom,
                                "separation": 0,
                            }
                        )

                        if len(info_per_line) > 1:
                            info_per_line[-1]["separation"] = (
                                info_per_line[-1]["top"] - info_per_line[-2]["bottom"]
                            )

                else:
                    info_per_line.append(
                        {"text": text, "top": top, "bottom": bottom, "separation": 0}
                    )

                    if len(info_per_line) > 1:
                        info_per_line[-1]["separation"] = (
                            info_per_line[-1]["top"] - info_per_line[-2]["bottom"]
                        )

                    line_num = current_line_num
                    text = image_data["text"][outer]
                    top = image_data["top"][outer]
                    bottom = image_data["top"][outer] + image_data["height"][outer]
                    word_num_visited = {image_data["word_num"][outer]}

        # We reconstruct the phrases with two things in mind:
        # If the separation between lines A and B is greater than 20, or
        # if the line height difference between them is greater than 5% of the largest one
        # and the separation between them is larger than 7,
        # lines A and B belong to different phrases
        phrase_reconstruction = [info_per_line[0]]
        candidate = {"text": "", "height": 0}
        for prev, next in zip(info_per_line, info_per_line[1:]):
            prev_text_height = prev["bottom"] - prev["top"]
            next_text_height = next["bottom"] - next["top"]

            if next["separation"] > 20 or (
                next["separation"] > 7
                and abs(prev_text_height - next_text_height)
                > max(prev_text_height, next_text_height) * 0.05
            ):
                phrase_reconstruction.append(next)
            else:
                i = len(phrase_reconstruction) - 1

                phrase_reconstruction[i]["text"] += f" {next['text']}"

                if (
                    next["bottom"] - next["top"]
                    > phrase_reconstruction[i]["bottom"]
                    - phrase_reconstruction[i]["top"]
                ):
                    phrase_reconstruction[i]["bottom"] = next["bottom"]
                    phrase_reconstruction[i]["top"] = next["top"]

        # We find the largest phrase which has between 5 and 20 words
        candidate = {"text": "", "height": 0}
        for line in phrase_reconstruction:
            line_height = line["bottom"] - line["top"]
            word_count = len(line["text"].split())

            # Ignore some random garbage values detected by OCR
            if line_height > 0.1 * image_data["top"][-1]:
                continue

            if line_height > candidate["height"] and word_count > 5 and word_count < 20:
                candidate["text"] = utils.sanitize_string(line["text"])
                candidate["height"] = line_height

        if candidate["text"] != "":
            return candidate["text"]
        return None


class BaseStrategy:
    priority: int

    def augment(self, document, source):
        raise NotImplementedError


class MetadataStrategy(BaseStrategy):
    """
    Extracts the metadata of the PDF (if any) and populates the Publication document.
    """

    priority = 1

    def augment(self, document, source):
        pdf = PdfFileReader(open(source.path, "rb"))
        info = pdf.getDocumentInfo()

        # XXX see if there's a way to get more information from the meatadata

        if info.author is not None:
            document.authors = [
                documents.publication.Author(name=utils.sanitize_string(author))
                for author in info.author.replace("; ", ", ").split(", ")
            ]
        if info.subject is not None:
            document.abstract = utils.sanitize_string(info.subject)

        if info.title is not None:
            document.title = utils.sanitize_string(info.title)

        return document


class PubMedStrategy(BaseStrategy):
    """
    Uses the different title parsers to extract the title from the PDF,
    searches PubMed with it, and populates the Publication document with the results.
    """

    priority = 2

    def __init__(self, **kargs):
        super().__init__(**kargs)
        self._title_parsers = sorted(
            list(utils.find_subclasses(BaseTitleParser)),
            key=lambda parser: parser.priority,
        )

    def augment(self, document, source):
        articles = []
        for title_parser in self._title_parsers:
            title = title_parser().get_title(source)
            if title is None:
                continue

            formatted_title = f"{title} [TITLE]"
            result = transformers.PubmedSourceCreatePublicationCollectionDocument(
                terms=[formatted_title], articles=5, hours=-1
            ).transform(source=sources.PubMed())
            articles = result.content

            if len(articles) == 0:
                continue

            # XXX find a way to fix this
            # Since PubMed is not returning the articles in the 'Best Match' order in which
            # they are displayed in the web, we order the results according to how similar
            # they are to the actual title we want
            articles.sort(
                key=lambda article: SequenceMatcher(
                    None,
                    title,
                    article.title,
                ).ratio(),
                reverse=True,
            )
            if (
                SequenceMatcher(
                    None,
                    title,
                    articles[0].title,
                ).ratio()
                > 0.95
            ):
                break
            else:
                articles = []
        if len(articles) == 0:
            return document

        best_match = articles[0]
        publication_fields = documents.Publication.__fields__

        for field in publication_fields:
            if best_match.__dict__[field] != publication_fields[field].default:
                document.__dict__[field] = articles[0].__dict__[field]
        return documents.Publication.new_from(source, **document.__dict__)


class Transformer(BaseTransformer):
    """
    Extracts information from the first page of a scientific publication
    in PDF format and returns a populated `Publication` document.
    """

    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        source: sources.PDF

    class OutputsModel(BaseModel):
        document: documents.Publication

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def __init__(self, **kargs):
        super().__init__(**kargs)
        self._strategies = sorted(
            list(utils.find_subclasses(BaseStrategy)),
            key=lambda strategy: strategy.priority,
        )

    def _is_complete(self, document):
        publication_fields = documents.Publication.__fields__
        for field, value in document:
            if field in ("type", "version", "content", "context"):
                continue
            if value == publication_fields[field].default:
                return False
        return True

    def transform(self, source: sources.PDF) -> documents.Publication:
        document = documents.Publication.new_from(source)

        for strategy in self._strategies:
            document = strategy().augment(document, source)
            if self._is_complete(document):
                return document

        return document
