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

# This code contains snippets and concepts from
# https://stackoverflow.com/questions/50829874/how-to-find-table-like-structure-in-image

import os
import cv2
import pytesseract
import numpy as np

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from .. import sources
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms an `Image` source into a `Tabular` document where the document
    contains all human-readable table structure from the source image.
    """

    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        source: sources.Image

    class OutputsModel(BaseModel):
        document: documents.Tabular

    arguments: Optional[ArgumentsModel]
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def text_from_rectangle(self, image, rectagle):
        # account for contour lines
        left = max(rectagle[0] - 1, 0)
        top = max(rectagle[1] - 1, 0)
        right = left + rectagle[2] + 1
        bottom = top + rectagle[3] + 1

        crop = image[top:bottom, left:right]
        text = pytesseract.image_to_string(crop, lang="eng", config="--psm 6")

        return text.strip()

    def preprocess_for_text(self, image):
        # remove colors
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # apply otsu and invert
        image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # remove horizontal lines
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
        finder = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=2)
        contours = cv2.findContours(finder, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        for contour in contours:
            cv2.drawContours(image, [contour], -1, (0, 0, 0), 2)

        # remove vertical lines
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
        finder = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=2)
        contours = cv2.findContours(finder, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        for contour in contours:
            cv2.drawContours(image, [contour], -1, (0, 0, 0), 3)

        # invert back
        image = cv2.bitwise_not(image)

        return image

    def preprocess_for_clusters(self, image):
        # remove colors
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # apply otsu and invert
        image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # remove horizontal lines
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
        finder = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=2)
        contours = cv2.findContours(finder, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        for contour in contours:
            cv2.drawContours(image, [contour], -1, (0, 0, 0), 2)

        # remove vertical lines
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
        finder = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=2)
        contours = cv2.findContours(finder, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        for contour in contours:
            cv2.drawContours(image, [contour], -1, (0, 0, 0), 3)

        # invert back
        image = cv2.bitwise_not(image)

        # dilate to cluster text
        cpy = image.copy()
        struct = cv2.getStructuringElement(cv2.MORPH_RECT, (16, 16))
        cpy = cv2.dilate(~cpy, struct, anchor=(-1, -1), iterations=1)
        image = ~cpy

        return image

    def preprocess_for_lines(self, image):
        # remove colors
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # apply otsu
        image = cv2.threshold(image, 255, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # dilate so lines can touch
        cpy = image.copy()
        struct = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        cpy = cv2.dilate(~cpy, struct, anchor=(-1, -1), iterations=1)
        image = ~cpy

        return image

    def overlaps_vertically(self, rectagle1, rectagle2):
        top1 = rectagle1[1]
        bottom1 = top1 + rectagle1[3]

        top2 = rectagle2[1]
        bottom2 = top2 + rectagle2[3]

        # do these rectangle overlap on the vertical axe?
        return not (top2 >= bottom1 or bottom2 <= top1)

    def overlaps_horizontally(self, rectagle1, rectagle2):
        left1 = rectagle1[0]
        right1 = left1 + rectagle1[2]

        left2 = rectagle2[0]
        right2 = left2 + rectagle2[2]

        # do these rectangle horizontal on the vertical axe?
        return not (left2 >= right1 or right2 <= left1)

    def overlaps(self, rectagle1, rectagle2):
        horizontal_overlap = self.overlaps_horizontally(rectagle1, rectagle2)
        vertical_overlap = self.overlaps_vertically(rectagle1, rectagle2)
        overlap = horizontal_overlap and vertical_overlap

        # do these rectangle overlap in both axes?
        return overlap

    def find_text_boxes(self, image):
        contours, hierarchy = cv2.findContours(
            image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )

        # find max area
        areas = [cv2.contourArea(contour) for contour in contours]
        max_area = max(areas)

        # filter contours that too close to max area
        filtered = []
        for index, contour in enumerate(contours):
            area = areas[index]
            # XXX need a better way to discard big areas
            if area <= (max_area * 0.5):
                box = cv2.boundingRect(contour)
                filtered.append(box)

        # merge boxes that are overlapping
        merged = []
        for box in filtered:
            found = [f for f in filtered if self.overlaps(f, box)]

            left = min([f[0] for f in found])
            top = min([f[1] for f in found])
            right = max([f[0] + f[2] for f in found])
            bottom = max([f[1] + f[3] for f in found])

            parent = (left, top, right - left, bottom - top)

            if parent not in merged:
                merged.append(parent)

        return merged

    def find_table_in_boxes(self, boxes, cell_threshold=10, min_columns=2):
        rows = {}
        cols = {}

        # clustering the bounding boxes by their positions
        for box in boxes:
            (x, y, w, h) = box
            col_key = x // cell_threshold
            row_key = y // cell_threshold
            cols[row_key] = [box] if col_key not in cols else cols[col_key] + [box]
            rows[row_key] = [box] if row_key not in rows else rows[row_key] + [box]

        # filtering out the clusters having less than 2 cols
        table_cells = list(filter(lambda r: len(r) >= min_columns, rows.values()))
        # sorting the row cells by x coord
        table_cells = [list(sorted(tb)) for tb in table_cells]
        # sorting rows by the y coord
        table_cells = list(sorted(table_cells, key=lambda r: r[0][1]))

        return table_cells

    def find_table_in_rectangles(self, rectangles):
        sorted_rectangles = sorted(rectangles, key=lambda q: (q[1], q[0]))

        # find anchor cell
        anchor = sorted_rectangles[0]

        # find columns and rows
        first_columns = [
            q for q in sorted_rectangles if self.overlaps_vertically(q, anchor)
        ]
        first_rows = [
            q for q in sorted_rectangles if self.overlaps_horizontally(q, anchor)
        ]

        # generate table based on previous columns and rows
        table = [[]]
        cells_by_columns = {}
        last_first_row = first_rows[0]

        for index, rectangle in enumerate(sorted_rectangles):
            if not self.overlaps_vertically(rectangle, last_first_row):
                table.append([])
                last_first_row = rectangle

            row = table[-1]
            first_column = next(
                c for c in first_columns if self.overlaps_horizontally(rectangle, c)
            )
            columns = cells_by_columns.get(first_column, [])

            # check if this cell can be merged with a previous cell from the same column and row
            if len(columns) >= 1:
                last_column_cell = cells_by_columns[first_column][-1]
                last_column_cell_row_index = (
                    row.index(last_column_cell) if last_column_cell in row else None
                )

                if last_column_cell_row_index is not None:
                    merged_left = min(rectangle[0], last_column_cell[0])
                    merged_top = min(rectangle[1], last_column_cell[1])
                    merged_right = max(
                        rectangle[0] + rectangle[2],
                        last_column_cell[0] + last_column_cell[2],
                    )
                    merged_bottom = max(
                        rectangle[1] + rectangle[3],
                        last_column_cell[1] + last_column_cell[3],
                    )

                    merged_rectangle = (
                        merged_left,
                        merged_top,
                        merged_right - merged_left,
                        merged_bottom - merged_top,
                    )

                    cells_by_columns[first_column][-1] = merged_rectangle
                    row[last_column_cell_row_index] = merged_rectangle

                    continue

            cells_by_columns[first_column] = columns + [rectangle]
            row.append(rectangle)

        return table

    def build_lines(self, table_cells):
        if table_cells is None or len(table_cells) <= 0:
            return [], []

        max_last_col_width_row = max(table_cells, key=lambda b: b[-1][2])
        max_x = max_last_col_width_row[-1][0] + max_last_col_width_row[-1][2]

        max_last_row_height_box = max(table_cells[-1], key=lambda b: b[3])
        max_y = max_last_row_height_box[1] + max_last_row_height_box[3]

        hor_lines = []
        ver_lines = []

        for box in table_cells:
            x = box[0][0]
            y = box[0][1]
            hor_lines.append((x, y, max_x, y))

        for box in table_cells[0]:
            x = box[0]
            y = box[1]
            ver_lines.append((x, y, x, max_y))

        (x, y, w, h) = table_cells[0][-1]
        ver_lines.append((max_x, y, max_x, max_y))
        (x, y, w, h) = table_cells[0][0]
        hor_lines.append((x, max_y, max_x, max_y))

        # fix lines with missing joints
        max_hor_line = max(hor_lines, key=lambda l: l[2] - l[0])
        ver_lines = sorted(ver_lines, key=lambda l: l[0])
        hor_lines = sorted(hor_lines, key=lambda l: l[1])

        for index, h_line in enumerate(hor_lines):
            # XXX use last seen v_line instead
            joint = next((l for l in ver_lines if h_line[0] == l[0]), None)
            if joint is None:
                fixed_line = (max_hor_line[0], h_line[1], max_hor_line[2], h_line[3])
                hor_lines[index] = fixed_line

        return hor_lines, ver_lines

    def debug(self, image, rectangles, name="debug.png"):
        for rectangle in rectangles:
            (x, y, w, h) = rectangle
            cv2.rectangle(image, (x, y), (x + w - 2, y + h - 2), (0, 0, 255), 1)
        cv2.imwrite(name, image)

    def extract(self, source):
        image = cv2.imread(str(source.path))

        pre_processed = self.preprocess_for_clusters(image)
        text_boxes = self.find_text_boxes(pre_processed)
        cells = self.find_table_in_boxes(text_boxes)
        hor_lines, ver_lines = self.build_lines(cells)

        # infer structrue
        height, width = image.shape[:2]
        canvas = 255 * np.ones(shape=[height, width, 3], dtype=np.uint8)

        # draw horizontal lines
        for line in hor_lines:
            [x1, y1, x2, y2] = line
            cv2.line(canvas, (x1, y1), (x2, y2), (255, 0, 0), 1)

        # draw vertical lines
        for line in ver_lines:
            [x1, y1, x2, y2] = line
            cv2.line(canvas, (x1, y1), (x2, y2), (255, 0, 0), 1)

        # pre-process canvas for better structure
        canvas = self.preprocess_for_lines(canvas)
        canvas_boxes = self.find_text_boxes(canvas)
        table = self.find_table_in_rectangles(canvas_boxes)

        # pre-process image for better text extraction
        image = self.preprocess_for_text(image)

        # extract text while building table
        table = [
            [self.text_from_rectangle(image, cell) for cell in row] for row in table
        ]

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
