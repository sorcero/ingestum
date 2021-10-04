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
    """

    type: Literal["biorxiv"] = "biorxiv"

    query: str
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

    def get_source(self, output_dir, cache_dir):
        return sources.Biorxiv()
