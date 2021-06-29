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
from ..utils import find_subclasses

__script__ = os.path.basename(__file__).replace(".py", "")
__transformers__ = tuple(list(find_subclasses(BaseTransformer)) + ["Transformer"])
__conditionals__ = tuple(find_subclasses(conditionals.base.BaseConditional))


class Transformer(BaseTransformer):
    """
    Transforms a `Collection` document into another `Collection` document where
    each invidual document is transformed if the document matches the given
    condition.

    :param conditional: Conditional object to decide whether to apply the given
        transformer
    :type conditional: conditionals.base.BaseConditional
    :param transformer: Transformer object to apply to each document
    :type transformer: BaseTransformer
    """

    class ArgumentsModel(BaseModel):
        conditional: Union[__conditionals__]
        transformer: Union[__transformers__]

    class InputsModel(BaseModel):
        collection: documents.Collection

    class OutputsModel(BaseModel):
        collection: documents.Collection

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def transform(self, collection: documents.Collection) -> documents.Collection:
        super().transform(collection=collection)

        content = []
        for document in collection.content:
            if self.arguments.conditional.evaluate(document) is True:
                content.append(self.arguments.transformer.transform(document))
            else:
                content.append(document.new_from(document))

        return collection.new_from(collection, content=content)


Transformer.ArgumentsModel.update_forward_refs()
Transformer.update_forward_refs()
