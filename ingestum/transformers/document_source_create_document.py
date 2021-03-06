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
from typing import Union, Optional
from typing_extensions import Literal

from .. import documents
from .. import sources
from .base import BaseTransformer
from ..utils import find_subclasses, get_document_from_path

__script__ = os.path.basename(__file__).replace(".py", "")
__documents__ = tuple(find_subclasses(documents.Base))


class Transformer(BaseTransformer):
    """
    Transforms an undefined document source into a proper document.
    """

    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        source: sources.Document

    class OutputsModel(BaseModel):
        document: Union[__documents__]

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def transform(self, source: sources.Document) -> Union[__documents__]:
        super().transform(source=source)

        return get_document_from_path(source.path)
