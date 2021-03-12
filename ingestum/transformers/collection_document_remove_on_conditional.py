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
from typing import Optional, Union
from typing_extensions import Literal

from .. import documents
from .. import conditionals
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")
__conditionals__ = tuple(conditionals.base.BaseConditional.__subclasses__())


class Transformer(BaseTransformer):
    """
    Transforms a Collection document into another Collection
    document where documents are removed if the document matches
    a given conditional.

    Parameters
    ----------
    conditional : Conditional
        Conditional object to determine whether to remove a document
    """

    class ArgumentsModel(BaseModel):
        conditional: Union[__conditionals__]

    class InputsModel(BaseModel):
        collection: documents.Collection

    class OutputsModel(BaseModel):
        collection: documents.Collection

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def transform(self, collection):
        super().transform(collection=collection)

        content = []
        for document in collection.content:
            if self.arguments.conditional.evaluate(document) is False:
                content.append(document.new_from(document))

        return collection.new_from(collection, content=content)
