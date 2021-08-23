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
import sys
import copy
import re
import tempfile
from enum import Enum
from functools import cmp_to_key

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

import cv2
import numpy as np
from pdf2image import convert_from_path
from pytesseract.pytesseract import image_to_string

from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTComponent
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator

from .. import documents
from .. import sources
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Layout(str, Enum):
    SINGLE = "single"
    MULTI = "multi"
    AUTO = "auto"


class CropArea(BaseModel):
    left: float
    top: float
    right: float
    bottom: float


class Transformer(BaseTransformer):
    """
    Transforms a `PDF` input source into a `Text` document where the Text
    document contains all human-readable text from the PDF, using a combination
    of text extraction and OCR techniques.

    :param first_page: First page to be used
    :type first_page: int
    :param last_page: Last page to be used
    :type last_page: int
    :param options: Dictionary with params for the underlying library
    :type options: dict
    :param tolerance: The margin of error, in pixels, of bounding box and text
        box coordinates when performing comparative PDF text ingestion.
    :type tolerance: int
    :param crop: Dictionary with left, top, right and bottom coordinates to be
        included from the page, expressed in percentages. E.g. ``top=0.1`` and
        ``bottom=0.9``, means everything that comes before that first ten
        percent and that last ten percent will be excluded. Note that the page
        is defined as the PDF MediaBox, which may be slightly larger than the
        viewable/printable CropBox displayed in PDF viewers.
    :type crop: CropArea
    :param layout:
        * ``single`` will re-order the text assuming a single column layout
        * ``multi`` will re-order the text assuming a multi column layout
        * ``auto`` will try to infer the text layout and re-order text accordingly
    :type layout: Layout
    """

    class ArgumentsModel(BaseModel):
        first_page: Optional[int] = None
        last_page: Optional[int] = None
        options: Optional[dict] = None
        tolerance: Optional[int] = 10
        crop: Optional[CropArea] = CropArea(top=0, bottom=1, left=0, right=1)
        layout: Optional[Layout] = "auto"

    class InputsModel(BaseModel):
        source: sources.PDF

    class OutputsModel(BaseModel):
        document: documents.Text

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def find_boxes(self, img):
        """Return a list of tuples of text boxes in the given image.
        The tuples are in the form (x, y, width, height).
        """
        # Invert the image
        inv_binary = cv2.threshold(
            img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )[1]

        # Remove horizontal lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        detected_lines = cv2.morphologyEx(
            inv_binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2
        )
        h_lines = cv2.findContours(
            detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        h_lines = h_lines[0] if len(h_lines) == 2 else h_lines[1]
        for line in h_lines:
            cv2.drawContours(inv_binary, [line], -1, (0, 0, 0), 2)
        inv_binary = inv_binary.astype(np.uint8)

        # Dilate text in image
        kernel = np.ones((5, 5), np.uint8)
        dilation = cv2.dilate(inv_binary, kernel, iterations=4)

        # Close holes in text boxes
        closing = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE, kernel, iterations=2)

        # Find bounding boxes
        contours, hierarchy = cv2.findContours(
            closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        boxes = []
        for contour in contours:
            boxes.append(cv2.boundingRect(contour))

        return boxes

    def sort(self, a, b):
        if a == b:
            return 0

        # If a line's column comes before the other then
        # the line comes first as well
        if a["column"] < b["column"]:
            return -1
        if a["column"] > b["column"]:
            return 1

        # If both lines are in the same line then the top
        # comes first
        if a["top"] < b["top"]:
            return -1
        if a["top"] > b["top"]:
            return 1

        return 0

    def sort_columns(self, a, b):
        if a == b:
            return 0

        # If a column above the other then comes first
        horizontal_overlap = not (a["left"] >= b["right"] or a["right"] <= b["left"])
        if horizontal_overlap:
            if a["top"] < b["top"]:
                return -1
            if a["top"] > b["top"]:
                return 1

        # If a column is to the left side of the other then comes first
        vertical_overlap = not (a["top"] >= b["bottom"] or a["bottom"] <= b["top"])
        if vertical_overlap:
            if a["left"] < b["left"]:
                return -1
            if a["left"] > b["left"]:
                return 1

        # If it's a clearly defined page layout then the horizontal position
        # takes precedence
        if self._layout == Layout.MULTI:
            if a["left"] < b["left"]:
                return -1
            if a["left"] > b["left"]:
                return 1
            if a["top"] < b["top"]:
                return -1
            if a["top"] > b["top"]:
                return 1
        else:
            if a["top"] < b["top"]:
                return -1
            if a["top"] > b["top"]:
                return 1
            if a["left"] < b["left"]:
                return -1
            if a["left"] > b["left"]:
                return 1

        return 0

    def similarity(self, element1, element2, distance, reference_distance):
        if element1 is None or element2 is None:
            return 0

        similarity = 0

        # Take into account the size / height of each line
        similarity += 1 - (
            abs(element1["size"] - element2["size"])
            / max([element1["size"], element2["size"]])
        )
        # The distance between them, giving preference to lines that are closer
        similarity += 1 if distance <= reference_distance else 0
        # Whether are both center
        similarity += 1 if element1["centered"] == element2["centered"] else 0
        # Whether are both all uppercase.
        similarity += 1 if element1["caps"] == element2["caps"] else 0

        # XXX all of these characteristics are equally weighted
        similarity /= 4

        return similarity

    def find_neighbour(self, rectangle, rectangles):
        # Traverse the page from top to bottom only including the lines
        # overlap with this one
        filtered_rectangles = [
            r
            for r in rectangles
            if not (r["left"] >= rectangle["right"] or r["right"] <= rectangle["left"])
        ]

        index = filtered_rectangles.index(rectangle)

        # Find the lines that come before and after
        after = filtered_rectangles[min([index + 1, len(filtered_rectangles) - 1])]
        before = filtered_rectangles[max([index - 1, 0])]

        # Calculate the distance to each
        before_distance = max(rectangle["top"] - before["bottom"], rectangle["size"])
        after_distance = max(after["top"] - rectangle["bottom"], rectangle["size"])
        min_distance = min(before_distance, after_distance)

        # Calculate the similarity to each
        before_similarity = self.similarity(
            rectangle, before, before_distance, min_distance * 2
        )
        after_similarity = self.similarity(
            rectangle, after, after_distance, min_distance * 2
        )

        # If any of these happen to be contained inside the current line, e.g. itself,
        # then consider it a neighbor
        before_contained = not (
            rectangle["left"] >= before["right"] or rectangle["right"] <= before["left"]
        ) and not (
            rectangle["top"] >= before["bottom"] or rectangle["bottom"] <= before["top"]
        )
        after_contained = not (
            rectangle["left"] >= after["right"] or rectangle["right"] <= after["left"]
        ) and not (
            rectangle["top"] >= after["bottom"] or rectangle["bottom"] <= after["top"]
        )

        neighbourhood = [rectangle]

        if before_contained:
            neighbourhood.append(before)
        if after_contained:
            neighbourhood.append(after)

        # Consider a neighbor only the lines that are identical
        if before_similarity == 1:
            neighbourhood.append(before)
        if after_similarity == 1:
            neighbourhood.append(after)

        return neighbourhood

    def overlaps(self, rect1, rect2):
        # Given two rectangles, determine if these overlap
        return not (
            rect2["left"] >= rect1["right"] or rect2["right"] <= rect1["left"]
        ) and not (rect2["top"] >= rect1["bottom"] or rect2["bottom"] <= rect1["top"])

    def find_column(self, rectangle, columns):
        # Find an existing column that overlaps with this rectangle / line
        column = next(
            ([c] for c in columns if self.overlaps(rectangle, c)),
            [],
        )

        return column

    def find_columns(self, rectangles):
        columns = []

        sorted_rectangles = sorted(rectangles, key=lambda r: (r["top"], r["left"]))

        # Find clusters of lines a.k.a columns
        for rectangle in sorted_rectangles:
            # Find neighbor lines
            neighbours = self.find_neighbour(rectangle, sorted_rectangles)
            # Find existing columns that contain neighbors
            found = next((self.find_column(n, columns) for n in neighbours), [])
            # Mix both
            found += neighbours

            # Create a new column that contains all of these
            left = min([f["left"] for f in found])
            top = min([f["top"] for f in found])
            right = max([f["right"] for f in found])
            bottom = max([f["bottom"] for f in found])

            column = {
                "left": left,
                "top": top,
                "right": right,
                "bottom": bottom,
                "text": found[0]["text"].strip() + rectangle["text"].strip(),
            }

            columns.append(column)

            # Remove all columns that were replaced by the new one
            for r in found:
                if r in columns:
                    columns.remove(r)

        return columns

    def detect_layout(self, columns):
        if self.arguments.layout == Layout.SINGLE:
            self._layout = Layout.SINGLE
            return

        if self.arguments.layout == Layout.MULTI:
            self._layout = Layout.MULTI
            return

        sorted_columns = sorted(columns, key=lambda r: (r["top"], r["left"]))

        # Find all columns that possibly overlap in the page
        rectangles = []
        for column in sorted_columns:
            left = sys.maxsize
            top = sys.maxsize
            right = 0
            bottom = 0

            for _column in sorted_columns:
                if (
                    _column["left"] >= column["right"]
                    or _column["right"] <= column["left"]
                ):
                    continue

                left = min([column["left"], _column["left"], left])
                top = min([column["top"], _column["top"], top])
                right = max([column["right"], _column["right"], right])
                bottom = max([column["bottom"], _column["bottom"], bottom])

            rectangle = {
                "left": left,
                "top": top,
                "right": right,
                "bottom": bottom,
            }

            rectangles.append(rectangle)

        # Find top level rectangles that contain all overlapping group of columns
        # so we can analize the global layout of the page
        layouts = []
        for rectangle in rectangles:

            layout_rectangle = {
                "left": sys.maxsize,
                "top": sys.maxsize,
                "right": 0,
                "bottom": 0,
            }

            for _rectangle in rectangles:
                if not self.overlaps(rectangle, _rectangle):
                    continue

                layout_rectangle = {
                    "left": min(
                        [
                            rectangle["left"],
                            _rectangle["left"],
                            layout_rectangle["left"],
                        ]
                    ),
                    "top": min(
                        [
                            rectangle["top"],
                            _rectangle["top"],
                            layout_rectangle["top"],
                        ]
                    ),
                    "right": max(
                        [
                            rectangle["right"],
                            _rectangle["right"],
                            layout_rectangle["right"],
                        ]
                    ),
                    "bottom": max(
                        [
                            rectangle["bottom"],
                            _rectangle["bottom"],
                            layout_rectangle["bottom"],
                        ]
                    ),
                }

            if layout_rectangle not in layouts:
                layouts.append(layout_rectangle)

        layout_sizes = [l["right"] - l["left"] for l in layouts]
        max_size = max(layout_sizes)
        min_size = min(layout_sizes)
        margin_size = max_size * 0.1

        # If there's only one global layout
        if len(layouts) == 1:
            self._layout = Layout.SINGLE
            return

        # If there's two global layouts but one is tinny in comparison, e.g. page number
        if len(layouts) == 2 and min_size < margin_size:
            self._layout = Layout.SINGLE
            return

        self._layout = Layout.MULTI

    def columnize(self, elements):
        """Finds all columns and sorts them to mimic LTR reading pattern."""
        if not elements:
            return []

        columns = self.find_columns(elements)
        self.detect_layout(columns)
        columns = sorted(columns, key=cmp_to_key(self.sort_columns))

        # Assign each line its corresponding column
        for element in elements:
            column = next(
                (
                    c
                    for c in columns
                    if element["left"] >= c["left"]
                    and element["top"] >= c["top"]
                    and element["right"] <= c["right"]
                    and element["bottom"] <= c["bottom"]
                ),
                None,
            )

            index = columns.index(column)
            element["column"] = index

        return elements

    def enrich(self, elements):
        """Add basic element characteristics to make layout detection easier."""
        if not elements:
            return elements

        page_left_margin = min([b["left"] for b in elements])
        page_right_margin = max([b["right"] for b in elements])

        for element in elements:
            # Is it centered?
            element_width = element["right"] - element["left"]
            element_center = element["left"] + (element_width / 2)

            page_width = element["page_width"]
            page_center = page_width / 2

            left_margin = element["left"] - page_left_margin
            right_margin = page_right_margin - element["right"]

            centered = (
                True
                if (
                    abs(page_center - element_center) < (page_width * 0.01)
                    and left_margin > (page_width * 0.01)
                    and right_margin > (page_width * 0.01)
                )
                else False
            )
            element["centered"] = centered

            # Element height/size
            element_height = element["bottom"] - element["top"]
            element["size"] = element_height

            # Is it all uppercase?
            element["caps"] = element["text"].isupper()

        return elements

    def sort_elements(self, elements, crop):
        """Sorts the given elements and returns a list of elements within the
        given crop coordinates."""

        # Remove elements outside of the crop
        elements = [
            b
            for b in elements
            if b["left"] >= crop.left
            and b["top"] >= crop.top
            and b["right"] <= crop.right
            and b["bottom"] <= crop.bottom
        ]

        elements = self.enrich(elements)
        elements = self.columnize(elements)
        elements = sorted(elements, key=cmp_to_key(self.sort))
        return elements

    def extract_ocr(self, img, box):
        """Extracts text in the given box using OCR."""
        x, y, width, height = box
        cropped = img[y : y + height, x : x + width]
        cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)

        # PSM 6 assumes a single uniform block of text
        text = image_to_string(cropped_rgb, config="--psm 6")
        text = re.sub(" +", " ", text.strip())
        return text

    def extract_pdf(self, page, layout, img_width, img_height, box):
        """Extracts embedded PostScript text in the given box."""
        x, y, width, height = box
        pdf_width, pdf_height = page.mediabox[2], page.mediabox[3]
        pdf_width_scaler = pdf_width / float(img_width)
        pdf_height_scaler = pdf_height / float(img_height)

        # We know that the text in this box is a single block of text without
        # columns so we sort each character individually to increase accuracy.
        chars = []
        for obj in layout:
            if not isinstance(obj, LTTextBox):
                continue
            for line in obj:
                if not isinstance(line, LTTextLine):
                    continue
                for char in line:
                    if not isinstance(char, LTComponent):
                        continue
                    left_scaled = char.bbox[0] / pdf_width_scaler
                    top_scaled = img_height - char.bbox[3] / pdf_height_scaler
                    right_scaled = char.bbox[2] / pdf_width_scaler
                    bottom_scaled = img_height - char.bbox[1] / pdf_height_scaler

                    if (
                        left_scaled > x - self.arguments.tolerance
                        and right_scaled < x + width + self.arguments.tolerance
                        and top_scaled > y - self.arguments.tolerance
                        and bottom_scaled < y + height + self.arguments.tolerance
                    ):
                        # We round the y-coordinate and the bbox of the line to
                        # ignore differences in individual character heights.
                        chars.append(
                            {
                                "x": char.bbox[2],
                                "y": round(line.bbox[1]),
                                "text": char.get_text(),
                            }
                        )

        chars.sort(key=lambda c: c["x"])
        chars.sort(key=lambda c: c["y"], reverse=True)

        text = ""
        line_y = chars[0]["y"] if len(chars) > 0 else 0
        for char in chars:
            # XXX PDFMiner newlines don't have bounding boxes so we can't
            # treat them as chars in a sort
            if line_y != char["y"]:
                text += "\n"
                line_y = char["y"]
            text += char["text"]
        # Remove consecutive spaces for consistency with OCR output.
        text = re.sub(" +", " ", text.strip())
        return text

    def merge_lists(self, ocr_words, pdf_words):
        """Merge lists of OCR-generated words and PDF-generated words.
        The merge algorithm relies on "anchors", or words that are identical
        between the OCR and PDF text. Using the anchors to line up equivalent
        text, we can then identify sections that have missing PDF text or
        misread OCR text.

        It assumes that the OCR output is complete (but not necessarily
        accurate) and that the PDF output is accurate (but not necessarily
        complete).

        XXX Known failure cases: Misread OCR text next to missing PDF text
        will default to PDF reading.
        """

        ocr_words.append("\n")
        pdf_words.append("\n")

        # Find the anchors
        anchors = []
        index_ocr = 0
        for index_pdf, word_pdf in enumerate(pdf_words):
            # Look for a match up to 10 words away
            if word_pdf in ocr_words[index_ocr : index_ocr + 10]:
                match_index_ocr = ocr_words.index(word_pdf, index_ocr)
                anchors.append((match_index_ocr, index_pdf))
                index_ocr = match_index_ocr
        if len(anchors) == 0:
            return ocr_words

        # Merge words based on the anchors
        index_ocr = 0
        index_pdf = 0
        merged = []
        for anchor in anchors:
            if anchor[0] == index_ocr and anchor[1] == index_pdf:
                # Exact match
                merged.append(pdf_words[anchor[1]])
            elif anchor[0] > index_ocr and anchor[1] == index_pdf:
                # Text missing from PDF
                merged.extend(ocr_words[index_ocr : anchor[0] + 1])
            elif anchor[0] > index_ocr and anchor[1] > index_pdf:
                # Misread text from OCR
                merged.extend(pdf_words[index_pdf : anchor[1] + 1])

            index_ocr = anchor[0] + 1
            index_pdf = anchor[1] + 1
        merged.extend(ocr_words[index_ocr:])

        return merged

    def merge(self, ocr_text, pdf_text):
        """Merges OCR-generated and PDF-generated text from the same box."""

        # Put exactly one newline and a space at the end of each line for
        # consistency and to maintain newlines after merge.
        ocr_text = re.sub("\s?\n+", "\n ", ocr_text)
        ocr_text = re.sub("\s\n\s", " ", ocr_text)
        pdf_text = re.sub("\s?\n+", "\n ", pdf_text)
        pdf_text = re.sub("\s\n\s", " ", pdf_text)

        ocr_words = ocr_text.split(" ")
        pdf_words = pdf_text.split(" ")

        merged = " ".join(self.merge_lists(ocr_words, pdf_words))
        merged = re.sub("\n\s", "\n", merged)

        return merged

    def is_overlapping(self, img, page, box, extractable):
        """Returns true if box overlaps with the extractable box."""
        x, y, width, height = box
        if (
            x >= extractable.left
            and x <= extractable.right
            and y >= extractable.top
            and y <= extractable.bottom
        ):
            return True

        if (
            x + width >= extractable.left
            and x + width <= extractable.right
            and y >= extractable.top
            and y <= extractable.bottom
        ):
            return True

        if (
            x >= extractable.left
            and x <= extractable.right
            and y + height >= extractable.top
            and y + height <= extractable.bottom
        ):
            return True

        if (
            x + width >= extractable.left
            and x + width <= extractable.right
            and y + height >= extractable.top
            and y + height <= extractable.bottom
        ):
            return True

        return False

    def debug(self, path, pageno, boxes, extractables, prefix="debug"):
        img = cv2.imread(path, 1)

        for box in boxes:
            x, y, width, height = box
            cv2.rectangle(img, (x, y), (x + width, y + height), (0, 255, 0), 2)

        for extractable in extractables:
            left = int(extractable.left)
            top = int(extractable.top)
            right = int(extractable.right)
            bottom = int(extractable.bottom)

            cv2.rectangle(img, (left, top), (right, bottom), (255, 0, 0), 2)

        cv2.imwrite(f"{prefix}.{pageno}.png", img)

    def extract(self, source, extractables=None, replacements=None):
        directory = tempfile.TemporaryDirectory()

        options = {}
        if self.arguments.options is not None:
            options = self.arguments.options

        first_page = self.arguments.first_page
        if first_page is None:
            first_page = 1

        last_page = self.arguments.last_page
        if last_page is None:
            last_page = source.get_pages()

        manager = PDFResourceManager()
        laparams = LAParams(**options)
        device = PDFPageAggregator(manager, laparams=laparams)
        interpreter = PDFPageInterpreter(manager, device)

        pagenos = set([x - 1 for x in range(first_page, last_page + 1)])
        pdf = open(source.path, "rb")
        pages = PDFPage.get_pages(
            pdf, pagenos=pagenos, caching=True, check_extractable=False
        )

        text = ""
        for pageno, page in enumerate(pages, start=first_page):
            interpreter.process_page(page)
            layout = device.get_result()

            path = convert_from_path(
                source.path,
                first_page=pageno,
                last_page=pageno,
                output_folder=directory.name,
                paths_only=True,
            )[0]
            img = cv2.imread(path, 0)
            img_width, img_height = img.shape[1], img.shape[0]
            pdf_width, pdf_height = page.mediabox[2], page.mediabox[3]
            pdf_width_scaler = pdf_width / float(img_width)
            pdf_height_scaler = pdf_height / float(img_height)

            IMG_CROP = CropArea(
                top=self.arguments.crop.top * img_height,
                bottom=self.arguments.crop.bottom * img_height,
                left=self.arguments.crop.left * img_width,
                right=self.arguments.crop.right * img_width,
            )

            boxes = self.find_boxes(img)

            _extractables = []
            _replacements = []
            content = extractables.content if extractables else []
            for index, extractable in enumerate(content):
                if pageno == extractable.pdf_context.page:
                    context = copy.deepcopy(extractables.content[index].pdf_context)
                    context.left = int(extractable.pdf_context.left / pdf_width_scaler)
                    context.top = int(extractable.pdf_context.top / pdf_height_scaler)
                    context.right = int(
                        extractable.pdf_context.right / pdf_width_scaler
                    )
                    context.bottom = int(
                        extractable.pdf_context.bottom / pdf_height_scaler
                    )
                    _extractables.append(context)

                    if replacements:
                        _replacements.append(replacements.content[index].content)

            # self.debug(path, pageno, boxes, _extractables)

            elements = []
            replaced = []
            for box in boxes:
                contained = False
                for index, _extractable in enumerate(_extractables):
                    if self.is_overlapping(img, page, box, _extractable):
                        contained = True
                        if not _replacements[index] in replaced:
                            replaced.append(_replacements[index])
                            elements.append(
                                {
                                    "left": _extractable.left,
                                    "right": _extractable.right,
                                    "top": _extractable.top,
                                    "bottom": _extractable.bottom,
                                    "page_width": pdf_width,
                                    "text": f"\n{_replacements[index]}\n\n",
                                }
                            )
                        break
                if contained:
                    continue

                ocr_text = self.extract_ocr(img, box)
                pdf_text = self.extract_pdf(page, layout, img_width, img_height, box)
                elements.append(
                    {
                        "left": box[0],
                        "right": box[0] + box[2],
                        "top": box[1],
                        "bottom": box[1] + box[3],
                        "page_width": pdf_width,
                        "text": self.merge(ocr_text, pdf_text)
                        if len(ocr_text) > 0 and not ocr_text.isspace()
                        else "",
                    }
                )

            for index, _extractable in enumerate(_extractables):
                if not _replacements[index] in replaced:
                    elements.append(
                        {
                            "left": _extractable.left,
                            "right": _extractable.right,
                            "top": _extractable.top,
                            "bottom": _extractable.bottom,
                            "page_width": pdf_width,
                            "text": f"\n{_replacements[index]}\n\n",
                        }
                    )

            sorted_elements = self.sort_elements(elements, IMG_CROP)
            sorted_text = [e["text"] for e in sorted_elements]
            text += "\n".join(sorted_text)

        return text

    def transform(self, source: sources.PDF) -> documents.Text:
        super().transform(source=source)

        return documents.Text.new_from(source, content=self.extract(source))
