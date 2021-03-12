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
import hashlib

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a Text document into a Passage document.
    """

    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        document: documents.Text

    class OutputsModel(BaseModel):
        document: documents.Passage

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    @staticmethod
    def extract_metadata(text):
        return {
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "tags": [],
            "anchors": [],
        }

    def transform(self, document):
        super().transform(document=document)

        content = document.content

        return documents.Passage.new_from(
            document, content=content, metadata=self.extract_metadata(content)
        )
