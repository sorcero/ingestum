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


import os

from typing import Optional, Union
from typing_extensions import Literal

from ... import utils
from . import credentials
from .base import BaseSource


class Source(BaseSource):

    type: Literal["remote"] = "remote"

    url: str
    url_placeholder: str = ""

    credential: Optional[Union[tuple(credentials.Base.__subclasses__())]] = None

    def get_source(self, output_dir, cache_dir=None):
        name, content = utils.fetch_and_preprocess(self.url, self.credential, cache_dir)
        path = os.path.join(output_dir, name)
        with open(path, "wb") as source:
            source.write(content)
        source_class = utils.get_source_by_name(self.type)
        return source_class(path=path)
