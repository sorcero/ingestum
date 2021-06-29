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
import math

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.layout import LTLine, LTCurve, LTContainer
from pdfminer.layout import LTTextLineHorizontal, LTTextLineVertical
from pdfminer.converter import PDFPageAggregator

from .. import sources
from .base import BaseTransformer
from .pdf_source_crop_extract import Transformer as STransformer

__script__ = os.path.basename(__file__).replace(".py", "")

TARGETS = (LTCurve, LTTextLineHorizontal, LTTextLineVertical)


class Transformer(BaseTransformer):
    """
    Extracts shapes from a `PDF` source to a given output directory.

    :param directory: Path to the directory where images will be extracted
    :type directory: str
    :param prefix: Prefix string used to name each extracted image
    :type prefix: str
    :param first_page: First page to be used
    :type first_page: int
    :param last_page: Last page to be used
    :type last_page: int
    """

    class ArgumentsModel(BaseModel):
        directory: Optional[str] = None
        prefix: Optional[str] = None
        first_page: Optional[int] = None
        last_page: Optional[int] = None

    class InputsModel(BaseModel):
        source: sources.PDF

    class OutputsModel(BaseModel):
        source: sources.PDF

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    @classmethod
    def collect(cls, objs, width, height):
        elements = []

        for obj in objs:
            if isinstance(obj, TARGETS):
                left = obj.x0
                top = height - obj.y1
                right = left + obj.width
                bottom = top + obj.height
                text = obj.get_text() if hasattr(obj, "get_text") else None

                # XXX some crazy PDF stuff for vertical lines
                is_vertical_line = obj.width < 1.0
                if isinstance(obj, LTLine) and is_vertical_line:
                    linewidth = obj.linewidth

                    # if linewidth data is bogus then minimize the damage
                    if linewidth > height:
                        if top < (height / 2.0):
                            linewidth = top
                        else:
                            linewidth = height - top

                    top = top - (linewidth / 2.0)
                    bottom = top + linewidth

                elements.append(
                    {
                        "left": left,
                        "top": top,
                        "right": right,
                        "bottom": bottom,
                        "text": text,
                    }
                )

            if isinstance(obj, LTContainer):
                elements += cls.collect(obj._objs, width, height)

        return elements

    @staticmethod
    def process(elements, page, width, height, rotate):
        extractables = []

        left = math.inf
        top = math.inf
        right = -math.inf
        bottom = -math.inf
        first_top = None
        last_bottom = None
        out_of_bounds = None

        for element in elements:
            if element["text"] is None:
                # accumulate the following edges of the potential shape
                if element["left"] < left:
                    left = element["left"]
                if element["top"] < top:
                    top = element["top"]
                if element["right"] > right:
                    right = element["right"]
                if element["bottom"] > bottom:
                    bottom = element["bottom"]

                # if this is the first horizontal line keep track of it
                if not first_top and element["right"] - element["left"] > 1.0:
                    first_top = element["top"]

                last_bottom = element["bottom"]

                out_of_width = next(
                    (pos for pos in [left, right] if not (0 <= pos <= width)), None
                )
                out_of_height = next(
                    (pos for pos in [top, bottom] if not (0 <= pos <= height)), None
                )
                out_of_bounds = out_of_width is not None or out_of_height is not None

            # if we find a non-shape element after seeing a shape
            if (
                last_bottom is not None
                and element["text"] is not None
                and not out_of_bounds
            ):
                if element["top"] < bottom:
                    continue

                extractables.append(
                    {
                        "page": page,
                        "width": width,
                        "height": height,
                        "left": left,
                        "top": first_top if first_top else top,
                        "right": right,
                        "bottom": last_bottom,
                        "rotate": rotate,
                    }
                )

                left = math.inf
                top = math.inf
                right = -math.inf
                bottom = -math.inf
                first_top = None
                last_bottom = None
                out_of_bounds = None

        if last_bottom is not None and not out_of_bounds:
            extractables.append(
                {
                    "page": page,
                    "width": width,
                    "height": height,
                    "left": left,
                    "top": first_top if first_top else top,
                    "right": right,
                    "bottom": last_bottom,
                    "rotate": rotate,
                }
            )

        return extractables

    def dump(self, source, extractable, index):
        # discard single lines
        if extractable["bottom"] - extractable["top"] < 1:
            return
        if extractable["right"] - extractable["left"] < 1:
            return

        # XXX workaronud pdftoppm issue with rotated pages
        width = extractable["width"]
        height = extractable["height"]
        if extractable["rotate"] % 360 != 0:
            height = extractable["width"]
            width = extractable["height"]

        name = "%s.%06d.%d.%d.%d.%d.%d" % (
            self.arguments.prefix,
            index,
            extractable["page"],
            extractable["left"],
            extractable["top"],
            extractable["right"],
            extractable["bottom"],
        )
        STransformer(
            directory=self.arguments.directory,
            prefix=name,
            page=extractable["page"],
            width=width,
            height=height,
            left=extractable["left"],
            top=extractable["top"],
            right=extractable["right"],
            bottom=extractable["bottom"],
        ).crop(source.path)

    def extract(self, source):
        manager = PDFResourceManager()
        device = PDFDevice(manager)
        laparams = LAParams(detect_vertical=True)
        device = PDFPageAggregator(manager, laparams=laparams)
        interpreter = PDFPageInterpreter(manager, device)

        first_page = self.arguments.first_page
        if first_page is None:
            first_page = 1

        last_page = self.arguments.last_page
        if last_page is None:
            last_page = source.get_pages()

        pagenos = set([x - 1 for x in range(first_page, last_page + 1)])

        pdf = open(source.path, "rb")
        pages = PDFPage.get_pages(
            pdf, pagenos=pagenos, caching=True, check_extractable=False
        )

        extractables = []
        for pageno, page in enumerate(pages, start=first_page):
            interpreter.process_page(page)
            layout = device.get_result()
            elements = self.collect(layout._objs, layout.width, layout.height)
            elements.sort(key=lambda e: (e["top"], e["left"]))
            extractables += self.process(
                elements, pageno, layout.width, layout.height, page.rotate
            )

        for index, extractable in enumerate(extractables):
            self.dump(source, extractable, index)
        pdf.close()

    def transform(self, source: sources.PDF) -> sources.PDF:
        super().transform(source=source)

        self.extract(source)

        return source
