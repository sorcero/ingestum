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
from bs4 import BeautifulSoup

from .. import documents
from .. import sources
from .biorxiv_source_create_publication_collection_document import (
    Transformer as BaseTransformer,
)

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a `Biorxiv` source into a `Collection` of `XML` documents.

    :param query: biorxiv search query
    :type query: str
    :param articles: The number of publications to retrieve
    :type articles: int
    :param hours: Hours to look back from now
    :type hours: int
    :param from_date: Lower limit for posted date
    :type from_date: str
    :param to_date: Upper limit for posted date
    :type to_date: str
    :param repo: name of the publications repository (biorxiv or medrxiv)
    :type repo: str
    :param filters: extra filters for the biorxiv search URL
    :type filters: dict
    :param abstract_title_query: Biorxiv search query limited to abstract and title
    :type abstract_title_query: str
    :param abstract_title_flags: Matching either match-any or match-all
    :type abstract_title_flags: str
    :param sort: Sorting order either publication-date or relevance-rank
    :type sort: str
    :param direction: For publication-date either ascending or descending
    :type direction: str
    """

    class ArgumentsModel(BaseModel):
        query: Optional[str] = ""
        articles: int
        hours: Optional[int] = -1
        from_date: Optional[str] = ""
        to_date: Optional[str] = ""
        repo: str = "biorxiv"
        filters: Optional[dict] = {}
        abstract_title_query: Optional[str] = ""
        abstract_title_flags: Optional[str] = ""
        sort: Optional[str] = ""
        direction: Optional[str] = ""

    arguments: ArgumentsModel

    type: Literal[__script__] = __script__

    def get_publication(self, xml, url):
        # handle XML
        soup = BeautifulSoup(xml, "lxml")

        # handle title
        title = ""
        if title_data := soup.find("article-title"):
            title = title_data.text

        # create XML doc
        return documents.XML.new_from(
            None,
            title=title,
            origin=url,
            content=xml,
        )

    def transform(self, source: sources.Biorxiv) -> documents.Collection:
        return super().transform(source=source)
