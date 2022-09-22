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
from .located import Source as BaseSource


class Source(BaseSource):
    """
    :param first_page: First page to be used
    :type first_page: int
    :param last_page: Last page to be used
    :type last_page: int
    """

    type: Literal["pdf"] = "pdf"

    first_page: Optional[int] = None
    first_page_placeholder = -1

    last_page: Optional[int] = None
    last_page_placeholder = -1

    def get_source(self, **kargs):
        return super().get_source(cls=sources.PDF, **kargs)
