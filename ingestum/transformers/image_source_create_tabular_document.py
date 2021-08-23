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

# This code contains snippets and concepts from
# https://github.com/eihli/image-table-ocr

import os
import cv2
from pytesseract import image_to_string

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from .. import sources
from .. import utils
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class BaseEngine(BaseModel):
    type: str = "base"

    def read(self, img, rect):
        raise NotImplementedError()


class PytesseractEngine(BaseEngine):
    type: str = "pytesseract"

    def read(self, img, rect):
        """Returns the text in the given cell using Tesseract OCR."""
        x, y, width, height = rect
        crop = img[y : y + height, x : x + width]
        output = image_to_string(crop)
        text = output.replace("\n", " ")
        text = text.strip()

        return text


class Transformer(BaseTransformer):
    """
    Transforms an `Image` source into a `Tabular` document where the document
    contains all human-readable table structure from the source image.

    :param process_background: Set True if table lines are the same color as
        the background.
    :type process_background: bool
    :param engine: The OCR engine to use. Default is ``pytesseract``.
    :type engine: str
    """

    class ArgumentsModel(BaseModel):
        process_background: Optional[bool] = False
        engine: str = "pytesseract"

    class InputsModel(BaseModel):
        source: sources.Image

    class OutputsModel(BaseModel):
        document: documents.Tabular

    arguments: Optional[ArgumentsModel]
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def preprocess_for_lines(self, img):
        """Returns an image consisting solely of table lines in white on a
        black background."""
        # Blurring helps reduce noise so we can isolate table lines.
        BLUR_KERNEL_SIZE = (17, 17)
        STD_DEV_X_DIRECTION = 0
        STD_DEV_Y_DIRECTION = 0
        blurred = cv2.GaussianBlur(
            img, BLUR_KERNEL_SIZE, STD_DEV_X_DIRECTION, STD_DEV_Y_DIRECTION
        )

        # Apply a binary threshold and invert if necessary to make table lines
        # white.
        MAX_COLOR_VAL = 255
        BLOCK_SIZE = 15
        SUBTRACT_FROM_MEAN = -2
        if not self.arguments.process_background:
            blurred = ~blurred
        img_bin = cv2.adaptiveThreshold(
            blurred,
            MAX_COLOR_VAL,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            BLOCK_SIZE,
            SUBTRACT_FROM_MEAN,
        )

        # Isolate table lines; lines will be in white for contour detection.
        SCALE = 10
        image_width, image_height = img_bin.shape
        horizontal_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, (int(image_width / SCALE), 1)
        )
        horizontally_opened = cv2.morphologyEx(
            img_bin, cv2.MORPH_OPEN, horizontal_kernel
        )
        vertical_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, (1, int(image_height / SCALE))
        )
        vertically_opened = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, vertical_kernel)

        horizontally_dilated = cv2.dilate(
            horizontally_opened, cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        )
        vertically_dilated = cv2.dilate(
            vertically_opened, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 60))
        )

        mask = horizontally_dilated + vertically_dilated

        return mask

    def find_cell_boundaries(self, mask):
        """Returns a list of cell bounding boxes in the form (x, y, w, h)."""
        # Find cell boundaries.
        contours, heirarchy = cv2.findContours(
            mask,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        perimeter_lengths = [cv2.arcLength(c, True) for c in contours]
        epsilons = [0.05 * p for p in perimeter_lengths]
        approx_polys = [
            cv2.approxPolyDP(c, e, True) for c, e in zip(contours, epsilons)
        ]
        bounding_rects = [cv2.boundingRect(a) for a in approx_polys]

        # Filter out rectangles that are too narrow or too short.
        MIN_RECT_WIDTH = 40
        MIN_RECT_HEIGHT = 15
        bounding_rects = [
            r
            for r in bounding_rects
            if MIN_RECT_WIDTH < r[2] and MIN_RECT_HEIGHT < r[3]
        ]

        # Remove the largest bounding rectangle (the entire table) so we only
        # OCR individual cells.
        largest_rect = max(bounding_rects, key=lambda r: r[2] * r[3])
        bounding_rects = [b for b in bounding_rects if b is not largest_rect]

        cells = [c for c in bounding_rects]
        return cells

    def sort_cells(self, cells):
        """Sorts cells into a 2D matrix, left to right and top to bottom."""

        def cell_in_same_row(c1, c2):
            c1_center = c1[1] + c1[3] - c1[3] / 2
            c2_bottom = c2[1] + c2[3]
            c2_top = c2[1]
            return c2_top < c1_center < c2_bottom

        def avg_height_of_center(row):
            centers = [y + h - h / 2 for x, y, w, h in row]
            return sum(centers) / len(centers)

        rows = []
        while cells:
            first = cells[0]
            rest = cells[1:]
            cells_in_same_row = sorted(
                [c for c in rest if cell_in_same_row(c, first)], key=lambda c: c[0]
            )

            row_cells = sorted([first] + cells_in_same_row, key=lambda c: c[0])
            rows.append(row_cells)
            cells = [c for c in rest if not cell_in_same_row(c, first)]

        rows.sort(key=avg_height_of_center)
        return rows

    def rectangularize(self, table):
        """Fills in missing cells to make the given table rectangular."""
        table_width = max([len(row) for row in table])
        for row in table:
            if len(row) < table_width:
                row.extend([""] * (table_width - len(row)))
        return table

    def filter(self, table):
        def is_row_filled(row):
            return any(row)

        def is_col_filled(table, col_index):
            return any([row[col_index] for row in table])

        table = [row for row in table if is_row_filled(row)]
        filtered_table = [
            [
                element
                for index, element in enumerate(row)
                if is_col_filled(table, index)
            ]
            for row in table
        ]
        return filtered_table

    def debug(self, source, cells, prefix="debug"):
        img = cv2.imread(source.path, 1)
        for c in cells:
            cv2.rectangle(img, (c[0], c[1]), (c[0] + c[2], c[1] + c[3]), (0, 255, 0), 2)
        cv2.imwrite(f"{prefix}.png", img)

    def extract(self, source):
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

        img = cv2.imread(source.path, 0)
        mask = self.preprocess_for_lines(img)
        cells = self.find_cell_boundaries(mask)
        # self.debug(source, cells)
        rows = self.sort_cells(cells)

        table = [[e.read(img, cell) for cell in row] for row in rows]
        table = self.rectangularize(table)
        table = self.filter(table)

        return table

    def transform(self, source: sources.Image) -> documents.Tabular:
        super().transform(source=source)

        title = source.get_metadata().get("ImageDescription", "")
        content = self.extract(source)
        rows = len(content)
        columns = len(content[0]) if rows else 0

        return documents.Tabular.new_from(
            source,
            title=title,
            content=content,
            rows=rows,
            columns=columns,
        )
