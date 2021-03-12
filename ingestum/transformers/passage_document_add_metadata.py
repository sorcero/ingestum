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

from .. import documents
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a Passage document into another Passage document
    where a given tag is added.

    Parameters
    ----------
    key : str
        key to be used as the passage metadata
    value : str
        value to be added to the passage metadata
    """

    class ArgumentsModel(BaseModel):
        key: str
        value: str

    class InputsModel(BaseModel):
        document: documents.Passage

    class OutputsModel(BaseModel):
        document: documents.Passage

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def append_metadata(self, metadata):
        retval = metadata.copy()
        value_list = list(
            set.union(set(getattr(retval, self.arguments.key)), {self.arguments.value})
        )
        value_list.sort()
        setattr(retval, self.arguments.key, value_list)

        return retval

    def transform(self, document):
        super().transform(document=document)

        metadata = self.append_metadata(document.metadata)

        return document.new_from(document, metadata=metadata)
