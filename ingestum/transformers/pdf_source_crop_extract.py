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
import tempfile

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal
from pdf2image import convert_from_path

from .. import sources
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")

SCALE = 4


class Transformer(BaseTransformer):
    """
    Extracts a cropped area from a PDF Source given an
    output directory.

    Parameters
    ----------
    directory : str
        Path to the directory where the image will be extracted
    prefix : str
        Prefix string used to name the extracted image
    page : int
        Page to be used
    width : int
        Width to be used for the page
    height : int
        Height to be used for the page
    left : float
        Left-most x-coordinate
    top : float
        Top-most y-coordinate
    right : float
        Right-most x-coordinate
    bottom : float
        Bottom-most y-coordinate
    """

    class ArgumentsModel(BaseModel):
        directory: str
        prefix: str
        page: int
        width: int
        height: int
        left: float
        top: float
        right: float
        bottom: float

    class InputsModel(BaseModel):
        source: sources.PDF

    class OutputsModel(BaseModel):
        source: sources.PDF

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def crop(self, path):
        directory = tempfile.TemporaryDirectory()

        images = convert_from_path(
            path,
            first_page=self.arguments.page,
            last_page=self.arguments.page,
            size=(self.arguments.width * SCALE, self.arguments.height * SCALE),
            output_folder=directory.name,
        )

        image = images[0]
        image = image.crop(
            (
                self.arguments.left * SCALE,
                self.arguments.top * SCALE,
                self.arguments.right * SCALE,
                self.arguments.bottom * SCALE,
            )
        )
        image.save(
            os.path.join(self.arguments.directory, "%s.png" % self.arguments.prefix),
            format="PNG",
        )

        for image in images:
            image.close()

        directory.cleanup()

    def transform(self, source):
        super().transform(source=source)

        self.crop(source.path)

        return source
