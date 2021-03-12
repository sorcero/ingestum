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

from .. import sources
from .base import BaseTransformer
from .pdf_source_crop_extract import Transformer as TTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a given crop area from a PDF Source into
    Image source.

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
    left : int
        Left-most x-coordinate
    top : int
        Top-most y-coordinate
    right : int
        Right-most x-coordinate
    bottom : int
        Bottom-most y-coordinate
    """

    class ArgumentsModel(BaseModel):
        directory: str
        prefix: str
        page: int
        width: int
        height: int
        left: int
        top: int
        right: int
        bottom: int

    class InputsModel(BaseModel):
        source: sources.PDF

    class OutputsModel(BaseModel):
        document: sources.Image

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def transform(self, source):
        super().transform(source=source)

        # XXX need to think of a general solution for tmp assets
        directory = self.arguments.directory
        if directory is None:
            directory = tempfile.mkdtemp()

        prefix = self.arguments.prefix
        if prefix is None:
            prefix = "crop"

        TTransformer(
            directory=directory,
            prefix=prefix,
            page=self.arguments.page,
            width=self.arguments.width,
            height=self.arguments.height,
            left=self.arguments.left,
            top=self.arguments.top,
            right=self.arguments.right,
            bottom=self.arguments.bottom,
        ).transform(source)

        path = os.path.join(directory, "%s.png" % prefix)
        source = sources.Image(path=path)

        return source
