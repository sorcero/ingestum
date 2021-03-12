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

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal
from pytesseract.pytesseract import image_to_string
from PIL import Image

from .. import documents
from .. import sources
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms an Image source into a Text document where
    the document contains all human-readable text from
    the source image.
    """

    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        source: sources.Image

    class OutputsModel(BaseModel):
        document: documents.Text

    type: Literal[__script__] = __script__
    arguments: Optional[ArgumentsModel]
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    @staticmethod
    def extract_text(source):
        return image_to_string(Image.open(source.path)).strip()

    def transform(self, source):
        super().transform(source=source)

        title = source.get_metadata().get("ImageDescription", "")

        return documents.Text.new_from(
            source, title=title, content=self.extract_text(source)
        )
