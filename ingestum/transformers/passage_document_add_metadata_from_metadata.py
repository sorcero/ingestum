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

from .base import BaseTransformer
from .. import documents

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a `Passage` document into another `Passage` document where a
    metadata entry is copied from another entry, e.g. tags are copied to anchors.

    :param source: metadata source for copy operation
    :type source: str
    :param target: metadata target for copy operation
    :type target: str
    """

    class ArgumentsModel(BaseModel):
        source: str
        target: str

    class InputsModel(BaseModel):
        document: documents.Passage

    class OutputsModel(BaseModel):
        document: documents.Passage

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def extract(self, metadata):
        retval = metadata.copy()
        value_list = list(
            set.union(
                set(getattr(retval, self.arguments.source)),
                set(getattr(retval, self.arguments.target)),
            )
        )
        value_list.sort()
        setattr(retval, self.arguments.target, value_list)

        return retval

    def transform(self, document: documents.Passage) -> documents.Passage:
        super().transform(document=document)

        return document.new_from(document, metadata=self.extract(document.metadata))
