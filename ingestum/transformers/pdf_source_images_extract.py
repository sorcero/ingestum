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
import numpy

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTImage, LTContainer

from .. import sources
from .base import BaseTransformer
from .pdf_source_crop_extract import Transformer as STransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Extracts images from a PDF Source to a given
    output directory.

    Parameters
    ----------
    directory : str
        Path to the directory where images will be extracted
    prefix : str
        Prefix string used to name each extracted image
    first_page : int
        First page to be used
    last_page : int
        Last page to be used
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

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def dump(self, index, image, source):
        prefix = "%s.%06d.%d.%d.%d.%d.%d" % (
            self.arguments.prefix,
            index,
            image["page"],
            image["left"],
            image["top"],
            image["right"],
            image["bottom"],
        )

        # XXX workaround sub-pixel thin images

        if image["left"] == image["right"]:
            image["left"] = numpy.clip(image["left"] - 1, 0, image["width"])
            image["right"] = numpy.clip(image["right"] + 1, 0, image["width"])

        if image["top"] == image["bottom"]:
            image["top"] = numpy.clip(image["top"] - 1, 0, image["height"])
            image["bottom"] = numpy.clip(image["bottom"] + 1, 0, image["height"])

        STransformer(
            directory=self.arguments.directory,
            prefix=prefix,
            page=image["page"],
            width=image["width"],
            height=image["height"],
            left=image["left"],
            top=image["top"],
            right=image["right"],
            bottom=image["bottom"],
        ).crop(source.path)

    def collect(self, objs, page, width, height):
        images = []

        for obj in objs:
            if isinstance(obj, LTImage):
                left = int(obj.x0)
                top = int(height - obj.y1)
                right = int(left + obj.width)
                bottom = int(top + obj.height)

                images.append(
                    {
                        "left": left,
                        "top": top,
                        "right": right,
                        "bottom": bottom,
                        "page": page,
                        "width": width,
                        "height": height,
                    }
                )

            if isinstance(obj, LTContainer):
                images += self.collect(obj._objs, page, width, height)

        return images

    def extract(self, source):
        self._counter = 0
        manager = PDFResourceManager()
        device = PDFPageAggregator(manager)
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

        images = []
        for pageno, page in enumerate(pages, start=first_page):
            interpreter.process_page(page)
            layout = device.get_result()
            images += self.collect(layout._objs, pageno, layout.width, layout.height)

        for index, image in enumerate(images):
            self.dump(index, image, source)
        pdf.close()

    def transform(self, source):
        super().transform(source=source)

        self.extract(source)

        return source
