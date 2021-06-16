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


from typing_extensions import Literal

from ... import utils

from .base import BaseSource


class Source(BaseSource):

    type: Literal["reddit"] = "reddit"

    search: str
    subreddit: str
    search_placeholder: str = ""
    subreddit_placeholder: str = ""

    def get_source(self, workspace):
        source_class = utils.get_source_by_name(self.type)
        return source_class(search=self.search, subreddit=self.subreddit)
