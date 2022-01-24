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


import os
import sys

from enum import Enum
from functools import cmp_to_key
from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.layout import LTContainer
from pdfminer.layout import LTTextLineHorizontal, LTTextBoxHorizontal
from pdfminer.layout import LTTextLineVertical, LTTextBoxVertical
from pdfminer.layout import LTImage, LTCurve
from pdfminer.converter import PDFPageAggregator

from .. import documents
from .. import sources
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")

TEXT_BOX_TARGETS = (LTTextBoxHorizontal, LTTextBoxVertical)
TEXT_LINE_TARGETS = (LTTextLineHorizontal, LTTextLineVertical)
NON_TEXT_TARGETS = (LTImage, LTCurve)
ITERABLE_TARGETS = LTContainer


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
    document contains all human-readable text from the PDF.

    :param first_page: First page to be used
    :type first_page: int
    :param last_page: Last page to be used
    :type last_page: int
    :param options: Dictionary with params for the underlying library
    :type options: dict
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
    """

    class ArgumentsModel(BaseModel):
        first_page: Optional[int] = None
        last_page: Optional[int] = None
        options: Optional[dict] = None
        crop: Optional[CropArea] = None
        layout: Optional[Layout] = "auto"

    class InputsModel(BaseModel):
        source: sources.PDF

    class OutputsModel(BaseModel):
        document: documents.Text

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

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
        if not elements:
            return []

        # Find all columns and sort them to mimic LTR reading pattern
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
        if not elements:
            return elements

        page_left_margin = min([e["left"] for e in elements])
        page_right_margin = max([e["right"] for e in elements])

        # Extract the most basic characteristics from each line so we can calculate similarity later
        for element in elements:
            # Is it centered justified?
            element_width = element["right"] - element["left"]
            element_center = element["left"] + (element_width / 2)

            page_width = element["width"]
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

            # Its vertical size / height
            size = element["bottom"] - element["top"]
            element["size"] = size

            # Is it all uppercase?
            element["caps"] = element["text"].isupper()

        return elements

    def filter(self, elements):
        filtered = []

        # Filter out noisy lines so we only work with human-visible lines.
        for element in elements:
            # Empty lines floating around
            if not element["text"].strip():
                continue

            # Lines that go outside of the page boundaries
            if (
                element["left"] < 0
                or element["right"] > element["width"]
                or element["top"] < 0
                or element["bottom"] > element["height"]
            ):
                continue

            # Artifacts from the PDF, e.g. watermarks sometimes come with ZERO width or height
            if (
                element["bottom"] - element["top"] <= 0
                or element["right"] - element["left"] <= 0
            ):
                continue

            # Lines that go outside the crop area
            if self.arguments.crop is not None:
                if element["left"] < self.arguments.crop.left * element["width"]:
                    continue
                if element["top"] < self.arguments.crop.top * element["height"]:
                    continue
                if element["right"] > self.arguments.crop.right * element["width"]:
                    continue
                if element["bottom"] > self.arguments.crop.bottom * element["height"]:
                    continue

            filtered.append(element)

        return filtered

    def collect(self, objs, height, width, extractables, replacements):
        elements = []

        for obj in objs:
            if isinstance(obj, TEXT_LINE_TARGETS + NON_TEXT_TARGETS):
                left = int(obj.x0)
                top = int(height - obj.y1)
                right = int(left + obj.width)
                bottom = int(top + obj.height)
                contained = False
                found = []

                for index, extractable in enumerate(extractables):
                    if (
                        left >= extractable.left
                        and top >= extractable.top
                        and right <= extractable.right
                        and bottom <= extractable.bottom
                    ):
                        contained = True
                        found.append(index)

                # XXX Originally limited to NON_TEXT_TARGETS
                if contained and replacements:
                    for index in found:
                        if extractables[index] in self._replaced:
                            continue

                        # mark this replacement as used so we don't repeat it
                        self._replaced.append(extractables[index])

                        elements.append(
                            {
                                "left": extractables[index].left,
                                "top": extractables[index].top,
                                "right": extractables[index].right,
                                "bottom": extractables[index].bottom,
                                "height": height,
                                "width": width,
                                "text": "\n%s\n\n" % replacements[index],
                            }
                        )

                if isinstance(obj, TEXT_LINE_TARGETS) and not contained:
                    elements.append(
                        {
                            "left": left,
                            "top": top,
                            "right": right,
                            "bottom": bottom,
                            "height": height,
                            "width": width,
                            "text": obj.get_text(),
                        }
                    )

            if isinstance(obj, ITERABLE_TARGETS):
                elements += self.collect(
                    obj._objs, height, width, extractables, replacements
                )

        return elements

    def extract(self, source, extractables=None, replacements=None):
        options = {}
        if self.arguments.options is not None:
            options = self.arguments.options

        self._replaced = []
        manager = PDFResourceManager()
        laparams = LAParams(**options)
        device = PDFPageAggregator(manager, laparams=laparams)
        interpreter = PDFPageInterpreter(manager, device)

        first_page = self.arguments.first_page
        if first_page is None or first_page <= 0:
            first_page = 1

        last_page = self.arguments.last_page
        if last_page is None or last_page <= 0:
            last_page = source.get_pages()

        pagenos = set([x - 1 for x in range(first_page, last_page + 1)])

        pdf = open(source.path, "rb")
        pages = PDFPage.get_pages(
            pdf, pagenos=pagenos, caching=True, check_extractable=False
        )

        text = ""
        for pageno, page in enumerate(pages, start=first_page):
            interpreter.process_page(page)
            layout = device.get_result()
            width = layout.width
            height = layout.height

            _extractables = []
            _replacements = []
            content = extractables.content if extractables else []
            for index, extractable in enumerate(content):
                if pageno == extractable.pdf_context.page:
                    _extractables.append(extractables.content[index].pdf_context)
                    if replacements:
                        _replacements.append(replacements.content[index].content)

            elements = self.collect(
                layout._objs, height, width, _extractables, _replacements
            )
            elements = self.filter(elements)

            if self.arguments.layout != Layout.ORIGINAL:
                elements = self.enrich(elements)
                elements = self.columnize(elements)
                elements = sorted(elements, key=cmp_to_key(self.sort))

            text += "".join(e["text"] for e in elements) + "\n"

        pdf.close()
        return text

    def transform(self, source: sources.PDF) -> documents.Text:
        super().transform(source=source)

        return documents.Text.new_from(source, content=self.extract(source))
