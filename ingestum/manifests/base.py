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


from pydantic import BaseModel
from typing import List, Union
from typing_extensions import Literal

from . import sources
from ..utils import find_subclasses

__sources__ = tuple(find_subclasses(sources.base.BaseSource))


class Manifest(BaseModel):
    """
    :param sources: Collection of sources to be included in the manifest
    :type sources: List[Union[__sources__]]
    """

    type: Literal["base"] = "base"
    sources: List[Union[__sources__]]
