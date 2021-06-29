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
from ..utils import find_subclasses

from .. import documents
from .. import conditionals
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")
__conditionals__ = tuple(find_subclasses(conditionals.base.BaseConditional))
__transformers__ = tuple(
    [
        t
        for t in find_subclasses(BaseTransformer)
        if ".passage_" in t.__module__ or ".text" in t.__module__
    ]
)


class Transformer(BaseTransformer):
    """
    Transforms a `Passage` document into another `Passage` document where the
    content is transformed by a given transformer if the passage matches a given
    conditional.

    :param conditional: Conditional object to termine whether to apply the
        transformer
    :type conditional: conditionals.base.BaseConditional
    :param transformer: Transformer object to apply to the document
    :type transformer: BaseTransformer
    """

    class ArgumentsModel(BaseModel):
        conditional: Union[__conditionals__]
        transformer: Union[__transformers__]

    class InputsModel(BaseModel):
        document: documents.Passage

    class OutputsModel(BaseModel):
        document: documents.Passage

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def transform(self, document: documents.Passage) -> documents.Passage:
        super().transform(document=document)

        if self.arguments.conditional.evaluate(document) is True:
            return self.arguments.transformer.transform(document)

        return document.copy()
