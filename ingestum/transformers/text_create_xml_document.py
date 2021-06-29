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

from ingestum import documents
from ingestum import transformers

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(transformers.base.BaseTransformer):
    """
    Transforms a `Text` document into an `XML` document.
    """

    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        document: documents.Text

    class OutputsModel(BaseModel):
        document: documents.XML

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    @staticmethod
    def extract_content(text):
        return text.replace("\\n", "\n").replace('\\"', '"')

    def transform(self, document: documents.Text) -> documents.XML:
        super().transform(document=document)

        return documents.XML.new_from(
            document,
            content=self.extract_content(document.content),
            title=document.title,
        )
