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

from .. import documents
from .. import sources
from .europepmc_source_create_publication_collection_document import (
    Transformer as TTransformer,
)

__logger__ = logging.getLogger("ingestum")
__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(TTransformer):
    """
    Transforms an `Europe PMC` source into a `XML` of `Publication` documents

    :param query: Europe PMC search query
    :type query: str
    :param articles: The number of publications to retrieve
    :type articles: int
    :param hours: Hours to look back from now
    :type hours: int
    :param from_date: Lower limit for publication date
    :type from_date: str
    :param to_date: Upper limit for publication date
    :type to_date: str
    :param cursor: Allows you to iterate through a search result set.
    :type cursor: str
    """

    class ArgumentsModel(BaseModel):
        query: Optional[str] = ""
        articles: int
        hours: Optional[int] = -1
        from_date: Optional[str] = ""
        to_date: Optional[str] = ""
        cursor: Optional[str] = ""

    arguments: ArgumentsModel

    type: Literal[__script__] = __script__

    def get_document(self, result):
        # Get provider id
        if id_node := result.find("id"):
            provider_id = id_node.text
        origin = self.get_origin(provider_id)

        return documents.XML.new_from(None, content=str(result), origin=origin)

    def transform(self, source: sources.EuropePMC) -> documents.Collection:
        return super().transform(source=source)
