# -*- coding: utf-8 -*-

#
# Copyright (c) 2020 Sorcero, Inc.
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


import math
import os
import sys
import tempfile
from enum import Enum
from functools import cmp_to_key

import cv2
from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from pdf2image import convert_from_path
from pdfminer.pdfpage import PDFPage
from pytesseract import image_to_data
from pytesseract import Output

from .. import documents
from .. import sources
from .. import utils
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class BaseEngine(BaseModel):
    type: str = "base"

    def read(self, img, rect, pdf_width, pdf_height):
        raise NotImplementedError()


class PytesseractEngine(BaseEngine):
    type: str = "pytesseract"

    def read(self, img, rect, pdf_width, pdf_height):
        """Returns a list of element dicts extracted from the given rectangle
        using Tesseract OCR."""
        x, y, width, height = rect
        crop = img[y : y + height, x : x + width]
        data = image_to_data(crop, output_type=Output.DICT)

        img_width, img_height = img.shape[1], img.shape[0]
        pdf_width_scaler = pdf_width / float(img_width)
        pdf_height_scaler = pdf_height / float(img_height)

        num_boxes = len(data["level"])
        elements = []
        for i in range(num_boxes):
            left = math.floor((data["left"][i] + x) * pdf_width_scaler)
            top = math.floor((data["top"][i] + y) * pdf_height_scaler)
            right = math.ceil(left + (data["width"][i] + x) * pdf_width_scaler)
            bottom = math.ceil(top + (data["height"][i] + y) * pdf_height_scaler)

            elements.append(
                {
                    "left": left,
                    "top": top,
                    "right": right,
                    "bottom": bottom,
                    "page_width": pdf_width,
                    "text": data["text"][i],
                }
            )

        elements = [e for e in elements if e["text"] != ""]
        return elements


class Layout(str, Enum):
    ORIGINAL = "original"
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
    document contains all human-readable text from the PDF, using OCR
    techniques.

    Requires ``INGESTUM_AZURE_CV_ENDPOINT`` and
    ``INGESTUM_AZURE_CV_SUBSCRIPTION_KEY`` environment variables for
    authentication if using Azure OCR.

    :param first_page: First page to be used
    :type first_page: int
    :param last_page: Last page to be used
    :type last_page: int
    :param crop: Dictionary with left, top, right and bottom coordinates to be
        included from the page, expressed in percentages. E.g. ``top=0.1`` and
        ``bottom=0.9``, means everything that comes before that first ten
        percent and that last ten percent will be excluded. Note that the page
        is defined as the PDF MediaBox, which may be slightly larger than the
        viewable/printable CropBox displayed in PDF viewers.
    :type crop: CropArea
    :param layout:
        * ``original`` will preserve the original PDF text order,
        * ``single`` will re-order the text assuming a single column layout
        * ``multi`` will re-order the text assuming a multi column layout
        * ``auto`` will try to infer the text layout and re-order text accordingly
    :type layout: Layout
    :param engine: The OCR engine to use. Default is ``pytesseract``.
    :type engine: str
    """

    class ArgumentsModel(BaseModel):
        first_page: Optional[int] = None
        last_page: Optional[int] = None
        crop: Optional[CropArea] = None
        layout: Optional[Layout] = "auto"
        engine: Optional[str] = "pytesseract"

    class InputsModel(BaseModel):
        source: sources.PDF

    class OutputsModel(BaseModel):
        document: documents.Text

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    @staticmethod
    def get_size(source):
        pdf = open(source.path, "rb")

        pages = PDFPage.get_pages(
            pdf, pagenos=None, caching=True, check_extractable=False
        )
        page = list(pages)[0]

        width = page.mediabox[2]
        height = page.mediabox[3]

        pdf.close()
        return (width, height)

    def make_lines(self, elements):
        """Combines adjacent elements into lines."""
        MAX_VERTICAL_DISTANCE = 5
        MAX_HORIZONTAL_DISTANCE = 10

        lines = []
        curr_line = None
        for element in elements:
            if curr_line is None:
                curr_line = element
            else:
                if (
                    curr_line["right"] - element["left"]
                ) <= MAX_HORIZONTAL_DISTANCE and abs(
                    curr_line["top"] - element["top"]
                ) <= MAX_VERTICAL_DISTANCE:
                    curr_line["text"] += " " + element["text"]
                    curr_line["right"] = element["right"]
                    curr_line["top"] = min(curr_line["top"], element["top"])
                    curr_line["bottom"] = max(curr_line["bottom"], element["bottom"])
                else:
                    lines.append(curr_line)
                    curr_line = element

        if curr_line is not None:
            lines.append(curr_line)

        return lines

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

        # If there's two global layouts but one is tiny in comparison, e.g. page number
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

    def extract(self, source):
        text = ""
        pdf = open(source.path, "rb")
        directory = tempfile.TemporaryDirectory()

        first_page = self.arguments.first_page
        if first_page is None:
            first_page = 1

        last_page = self.arguments.last_page
        if last_page is None:
            last_page = source.get_pages()

        pdf_width, pdf_height = self.get_size(source)

        text = ""
        for page in range(first_page, last_page + 1):
            path = convert_from_path(
                source.path,
                first_page=page,
                last_page=page,
                output_folder=directory.name,
                paths_only=True,
            )[0]
            img = cv2.imread(path)
            img_width, img_height = img.shape[1], img.shape[0]

            if self.arguments.crop is not None:
                crop_left = int(self.arguments.crop.left * img_width)
                crop_top = int(self.arguments.crop.top * img_height)
                crop_width = int(self.arguments.crop.right * img_width - crop_left)
                crop_height = int(self.arguments.crop.bottom * img_height - crop_top)
                rect = [crop_left, crop_top, crop_width, crop_height]
            else:
                rect = [0, 0, img_width, img_height]

            # Import all OCR engine classes, including plugins
            engine_classes = utils.find_subclasses(BaseEngine)
            Engine = next(
                (
                    e
                    for e in engine_classes
                    if e.__fields__["type"].default == self.arguments.engine
                ),
                None,
            )
            if Engine is None:
                raise ValueError(f"{self.arguments.engine} does not exist")
            e = Engine()

            elements = e.read(img, rect, pdf_width, pdf_height)
            elements = self.make_lines(elements)
            if self.arguments.layout != Layout.ORIGINAL:
                elements = self.enrich(elements)
                elements = self.columnize(elements)
                elements = sorted(elements, key=cmp_to_key(self.sort))

            text += "\n".join(e["text"] for e in elements) + "\n"
            os.remove(path)

        directory.cleanup()
        pdf.close()
        return text

    def transform(self, source: sources.PDF) -> documents.Text:
        super().transform(source=source)

        return documents.Text.new_from(source, content=self.extract(source))
