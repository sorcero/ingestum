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


from typing import Optional
from typing_extensions import Literal

from ... import sources
from .base import BaseSource


class Source(BaseSource):
    """
    :param search: The search string to pass to a Reddit query, e.g., "python"
        https://www.reddit.com/search/?q=python
    :type search: str
    :param subreddit: Limit search results to the subreddit if provided
    :type subreddit: str
    :param sort: The sorting criteria for the search
        The options are: ``"relevance"``, ``"hot"``, ``"new"``, ``"top"``,
        ``"comments"``; defaults to ``"relevance"``
    :type sort: str
    :param count: The number of results to try and retrieve (defaults to 100)
    :type count: Optional[int]
    """

    type: Literal["reddit"] = "reddit"

    search: str
    search_placeholder = ""

    subreddit: Optional[str]
    subreddit_placeholder = ""

    sort: Optional[str]
    sort_placeholder = ""

    count: Optional[int] = 100
    count_placeholder = -1

    def get_source(self, output_dir, cache_dir):
        return sources.Reddit(context=self.context)
