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


from typing import List, Optional
from typing_extensions import Literal

from ... import sources
from .base import BaseSource


class Source(BaseSource):
    """
    :param search: The search string to pass to a twitter query, e.g., Epiduo
        https://twitter.com/search?q=Epiduo
    :type search: str
    :param tags: The list of tags to pull from each tweet
    :type tags: Optional[List[str]]
    :param count: The number of results to try and retrieve (defaults to 100)
    :type count: Optional[int]
    :param sort: Type of search results you would prefer to receive
        The options are: ``"recent"``, ``"popular"``, ``"mixed"``; defaults to ``"recent"``
    :type sort: Optional[str]
    """

    type: Literal["twitter"] = "twitter"

    search: str
    search_placeholder = ""

    tags: Optional[List[str]] = []
    tags_placeholder = []

    count: Optional[int]
    count_placeholder = -1

    sort: Optional[str]
    sort_placeholder = ""

    def get_source(self, output_dir, cache_dir):
        return sources.Twitter()
