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

import logging

from typing_extensions import Literal


from .base import BaseLocation

__logger__ = logging.getLogger("ingestum")


class Location(BaseLocation):
    """
    :param path: Path to location in filesystem
    :type path: str
    """

    type: Literal["local"] = "local"

    path: str

    @property
    def uri(self):
        return f"file://{self.path}"

    def fetch(self, output_dir=None, cache_dir=None):
        __logger__.debug("re-using", extra={"props": {"source": self.path}})
        return self.path
