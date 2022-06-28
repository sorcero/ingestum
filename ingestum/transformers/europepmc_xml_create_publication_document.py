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
import logging

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal
from bs4 import BeautifulSoup

from .. import documents
from .base import BaseTransformer
from .europepmc_source_create_publication_collection_document import (
    Transformer as TTransformer,
)
from .europepmc_source_create_publication_collection_document import (
    ENDPOINTS as ENDPOINTS,
)

__logger__ = logging.getLogger("ingestum")
__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(TTransformer):
    """
    Transforms an `Europe PMC` XML document into a `Publication` document.

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
        self.search_endpoint = ENDPOINTS.get("EUROPEPMC_SEARCH_ENDPOINT")
        self.article_endpoint = ENDPOINTS.get("EUROPEPMC_ARTICLE_ENDPOINT")
        soup = BeautifulSoup(source.content, "xml")
        result = soup.find("result")

        publication = self.get_document(result)

        return publication
