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
import re
import tempfile

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
        percent and that last ten percent will be excluded.
    :type crop: CropArea
    """

    class ArgumentsModel(BaseModel):
        first_page: Optional[int] = None
        last_page: Optional[int] = None
        options: Optional[dict] = None
        tolerance: Optional[int] = 10
        crop: Optional[CropArea] = CropArea(top=0, bottom=1, left=0, right=1)

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

    def is_single_column(self, boxes, box):
        """Returns true if there are no other boxes that overlap the vertical
        span of the given box.
        """
        x, y, width, height = box
        overlaps = [b for b in boxes if b[1] < y + height and b[1] + b[3] > y]
        if len(overlaps) > 1:
            return False
        return True

    def sort_columns(self, boxes, pdf_width):
        """Roughly sorts in column order (go down one column then go to the top
        of the next). Coordinates are rounded to the nearest 1/12 of the page.

        XXX Assumes there won't be more than 12 columns on a given page.
        """
        tolerance_factor = pdf_width / 12
        boxes.sort(key=lambda b: round(b[1] / tolerance_factor))
        boxes.sort(key=lambda b: round(b[0] / tolerance_factor))
        return boxes

    def sort_boxes(self, boxes, crop, pdf_width):
        """Sorts the given boxes and returns the sorted boxes if they are
        within the given crop coordinates."""
        sorted_boxes = []

        boxes.sort(key=lambda x: x[1])
        column_boxes = []
        boxes = [
            b
            for b in boxes
            if b[0] >= crop.left
            and b[1] >= crop.top
            and b[0] + b[2] <= crop.right
            and b[1] + b[3] <= crop.bottom
        ]

        for box in boxes:
            x, y, width, height = box

            if self.is_single_column(boxes, box):
                # Multi-column section ended, sort and add to sorted boxes
                if len(column_boxes) > 0:
                    sorted_boxes.extend(self.sort_columns(column_boxes, pdf_width))
                    column_boxes = []
                sorted_boxes.append(box)
            else:
                column_boxes.append(box)
        if len(column_boxes) > 0:
            sorted_boxes.extend(self.sort_columns(column_boxes, pdf_width))

        return sorted_boxes

    def extract_ocr(self, img, index, box):
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

    def debug(self, img, pageno, boxes, prefix="debug"):
        for box in boxes:
            x, y, width, height = box
            cv2.rectangle(img, (x, y), (x + width, y + height), (0, 255, 0), 2)
        cv2.imwrite(f"{prefix}.{pageno}.png", img)

    def extract(self, source):
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
            img_width = img.shape[1]
            img_height = img.shape[0]

            IMG_CROP = CropArea(
                top=self.arguments.crop.top * img_height,
                bottom=self.arguments.crop.bottom * img_height,
                left=self.arguments.crop.left * img_width,
                right=self.arguments.crop.right * img_width,
            )

            boxes = self.find_boxes(img)
            boxes = self.sort_boxes(boxes, IMG_CROP, page.mediabox[2])

            for index, box in enumerate(boxes):
                # self.debug(img, pageno, boxes)
                ocr_text = self.extract_ocr(img, index, box)
                pdf_text = self.extract_pdf(page, layout, img_width, img_height, box)
                if len(ocr_text) > 0 and not ocr_text.isspace():
                    text += self.merge(ocr_text, pdf_text)

        return text

    def transform(self, source: sources.PDF) -> documents.Text:
        super().transform(source=source)

        return documents.Text.new_from(source, content=self.extract(source))
