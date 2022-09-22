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

from typing import Optional
from typing_extensions import Literal

from ... import sources
from .base import BaseSource


class Source(BaseSource):
    """
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
    :param full_text: Extract the full text article if set to True (defaults to False)
    :type full_text: bool
    :param abstract_title_query: Biorxiv search query limited to abstract and title
    :type abstract_title_query: str
    :param abstract_title_flags: Matching either match-any or match-all
    :type abstract_title_flags: str
    :param sort: Sorting order either publication-date or relevance-rank
    :type sort: str
    :param direction: For publication-date either ascending or descending
    :type direction: str
    """

    type: Literal["biorxiv"] = "biorxiv"

    query: Optional[str] = ""
    query_placeholder = ""

    articles: int
    articles_placeholder = -1

    hours: Optional[int] = -1
    hours_placeholder = -1

    from_date: Optional[str] = ""
    from_date_placeholder = ""

    to_date: Optional[str] = ""
    to_date_placeholder = ""

    repo: str
    repo_placeholder = ""

    filters: Optional[dict] = {}
    filters_placeholder = {}

    full_text: Optional[bool] = False
    full_text_placeholder = False

    abstract_title_query: Optional[str] = ""
    abstract_title_query_placeholder = ""

    abstract_title_flags: Optional[str] = ""
    abstract_title_flags_placeholder = ""

    sort: Optional[str] = ""
    sort_placeholder: Optional[str] = ""

    direction: Optional[str] = ""
    direction_placeholder: Optional[str] = ""

    cursor: Optional[int] = 0
    cursor_placeholder: Optional[int] = 0

    def get_source(self, output_dir, cache_dir):
        return sources.Biorxiv(context=self.context)
