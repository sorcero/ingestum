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


from typing import List, Optional
from typing_extensions import Literal

from ... import sources
from .base import BaseSource


class Source(BaseSource):

    type: Literal["pubmed"] = "pubmed"

    terms: List[str]
    terms_placeholder = []

    articles: int
    articles_placeholder = -1

    hours: Optional[int] = None
    hours_placeholder = -1

    def get_source(self, output_dir=None):
        return sources.PubMed()
