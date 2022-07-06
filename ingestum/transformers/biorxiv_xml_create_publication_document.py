# -*- coding: utf-8 -*-

#
# Copyright (c) 2022 Sorcero, Inc.
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
from .biorxiv_source_create_publication_collection_document import (
    Transformer as TTransformer,
)
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(TTransformer):
    """
    Transforms a `Biorxiv` XML into a `Publication` document

    :param repo: name of the publications repository (biorxiv or medrxiv)
    :type repo: str
    :param full_text: Extract the full text article if set to True (defaults to False)
    :type full_text: bool
    """

    class ArgumentsModel(BaseModel):
        full_text: Optional[bool] = False

    class InputsModel(BaseModel):
        source: documents.XML

    class OutputsModel(BaseModel):
        document: documents.Publication

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def transform(self, source: documents.XML) -> documents.Publication:
        BaseTransformer.transform(self, source=source)

        return self.get_publication(source.content, source.origin)
