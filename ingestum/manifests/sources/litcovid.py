# -*- coding: utf-8 -*-

#
# Copyright (c) 2021 Sorcero, Inc.
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


from typing_extensions import Literal
from typing import Optional

from ... import sources
from .pubmed import Source as BaseSource


class Source(BaseSource):
    """
    :param terms: PubMed queries
    :type terms: list
    :param articles: The number of publications to retrieve
    :type articles: int
    :param hours: Hours to look back from now
    :type hours: int
    :param from_date: Lower entrez date range limit
    :type from_date: str
    :param to_date: Upper entrez date range limit
    :type to_date: str
    :param query_string: Pre-formatted query string
    :type query_string: str
    :param sort: The sorting criteria for the search
        The options are: ``"_id desc"``, ``"score desc"``, ``"date desc"``; defaults to ``"score desc"``
    :type sort: Optional[str]
    """

    type: Literal["litcovid"] = "litcovid"

    query_string: str
    query_string_placeholder = ""

    sort: Optional[str] = "score desc"
    sort_placeholder = ""

    def get_source(self, output_dir, cache_dir):
        return sources.LitCovid()
