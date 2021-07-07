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

    type: Literal["html"] = "html"

    # don't confuse with location, this is only for downloading related assets
    url: Optional[str]
    url_placeholder: str = ""

    target: str
    target_placeholder: str = ""

    def get_source(self, output_dir, cache_dir):
        path = self.location.fetch(output_dir, cache_dir)
        return sources.HTML(path=path)
