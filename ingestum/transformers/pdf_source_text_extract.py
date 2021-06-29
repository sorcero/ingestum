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
import re

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.layout import LTContainer
from pdfminer.layout import LTTextBoxHorizontal
from pdfminer.layout import LTTextBoxVertical
from pdfminer.converter import PDFPageAggregator

from .. import sources
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Extracts text from a `PDF` source to a given output directory.

    :param directory: Path to the directory where images will be extracted
    :type directory: str
    :param prefix: Prefix string used to name each extracted image
    :type prefix: str
    :param first_page: First page to be used
    :type first_page: int
    :param last_page: Last page to be used
    :type last_page: int
    :param options: Dictionary with params for the underlying library
    :type options: dict
    :param regexp: Regular expression to filter extract text
    :type regexp: str
    """

    class ArgumentsModel(BaseModel):
        directory: Optional[str] = None
        prefix: Optional[str] = None
        first_page: Optional[int] = None
        last_page: Optional[int] = None
        options: Optional[dict] = None
        regexp: Optional[str] = None

    class InputsModel(BaseModel):
        source: sources.PDF

    class OutputsModel(BaseModel):
        source: sources.PDF

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def dump(self, index, text):
        name = "%s.%06d.%d.%d.%d.%d.%d" % (
            self.arguments.prefix,
            index,
            text["page"],
            text["left"],
            text["top"],
            text["right"],
            text["bottom"],
        )
        path = os.path.join(self.arguments.directory, "%s.txt" % name)
        with open(path, "w") as file:
            file.write(text["content"])

    def collect(self, objs, page, width, height):
        texts = []

        for obj in objs:
            if isinstance(obj, (LTTextBoxHorizontal, LTTextBoxVertical)):
                match = self._pattern.search(obj.get_text())
                if match is None:
                    continue

                left = int(obj.x0)
                top = int(height - obj.y1)
                right = int(left + obj.width)
                bottom = int(top + obj.height)
                texts.append(
                    {
                        "left": left,
                        "top": top,
                        "right": right,
                        "bottom": bottom,
                        "page": page,
                        "content": match.group(1),
                    }
                )

            if isinstance(obj, LTContainer):
                texts += self.collect(obj._objs, page, width, height)

        return texts

    def extract(self, source):
        self._pattern = re.compile(self.arguments.regexp, re.MULTILINE)

        options = {}
        if self.arguments.options is not None:
            options = self.arguments.options

        manager = PDFResourceManager()
        laparams = LAParams(**options)
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

        texts = []
        for pageno, page in enumerate(pages, start=first_page):
            interpreter.process_page(page)
            layout = device.get_result()
            texts += self.collect(layout._objs, pageno, layout.width, layout.height)

        for index, text in enumerate(texts):
            self.dump(index, text)
        pdf.close()

    def transform(self, source: sources.PDF) -> sources.PDF:
        super().transform(source=source)

        self.extract(source)

        return source
