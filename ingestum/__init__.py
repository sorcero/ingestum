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
import json_logging
import logging

json_logging.init_non_web(enable_json=True)

# https://docs.python.org/3/howto/logging.html#logging-levels
__level__ = "DEBUG" if os.environ.get("INGESTUM_DEBUG") else "INFO"

__logger__ = logging.getLogger("ingestum")
__logger__.setLevel(level=getattr(logging, __level__))
__logger__.addHandler(logging.StreamHandler())
