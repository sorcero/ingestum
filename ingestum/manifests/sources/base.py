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

from typing import Union, Optional
from typing_extensions import Literal

from pydantic import BaseModel

from . import destinations
from ...utils import find_subclasses

__destinations__ = tuple(find_subclasses(destinations.base.BaseDestination))


class BaseSource(BaseModel):
    """
    :param id: Manifest source ID
    :type id: str
    :param pipeline: Pipeline name
    :type pipeline: str
    :param destination: Destination of manifest results
    :type destination: Union[__destinations__]
    """

    type: Literal["base"] = "base"
    id: str
    pipeline: str
    destination: Union[__destinations__]
    context: Optional[dict]

    def get_source(self, output_dir, cache_dir):
        raise NotImplementedError
