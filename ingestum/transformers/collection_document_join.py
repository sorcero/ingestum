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
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")
__transformers__ = tuple(
    [
        t
        for t in find_subclasses(BaseTransformer)
        if "merge" in t.__module__ or "join" in t.__module__
    ]
)


class Transformer(BaseTransformer):
    """
    Transforms a Collection into one single document
    given a transformer to handle the join operation.

    Parameters
    ----------
    transformer : Transformer
        Transformer object with the join logic for the specific document type
    """

    class ArgumentsModel(BaseModel):
        transformer: Union[__transformers__]

    class InputsModel(BaseModel):
        collection: documents.Collection

    class OutputsModel(BaseModel):
        document: documents.Base

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def transform(self, collection):
        super().transform(collection=collection)

        document = collection.content[0]
        document = document.new_from(document, pdf_context=None)

        for _document in collection.content[1:]:
            document = self.arguments.transformer.transform(document, _document)

        return document
