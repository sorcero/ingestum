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
from typing import Optional, Union, TypeVar
from typing_extensions import Literal

from .. import documents
from .base import BaseTransformer

TransformerType = TypeVar("Transformer")

__script__ = os.path.basename(__file__).replace(".py", "")
__transformers__ = tuple(BaseTransformer.__subclasses__() + [TransformerType])


class Transformer(BaseTransformer):
    """
    Transforms a Collection document into another Collection
    document where each invidual document is transformed by
    a given transformer.

    Parameters
    ----------
    transformer : Transformer
        Transformer object to apply to each document
    """

    class ArgumentsModel(BaseModel):
        transformer: Union[__transformers__]

    class InputsModel(BaseModel):
        collection: documents.Collection

    class OutputsModel(BaseModel):
        document: documents.Collection

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def __init__(self, **kargs):
        super().__init__(**kargs)

    def transform(self, collection):
        super().transform(collection=collection)

        content = []
        for document in collection.content:
            content.append(self.arguments.transformer.transform(document))

        return collection.new_from(collection, content=content)
