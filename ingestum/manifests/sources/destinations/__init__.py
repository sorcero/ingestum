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

import sys

from ingestum.plugins import manager

from . import base
from . import void
from . import local
from . import remote
from . import google_datalake

Void = void.Destination
Local = local.Destination
Remote = remote.Destination
GoogleDatalake = google_datalake.Destination

# Load plugins
manager.default.register(
    sys.modules[__name__], "manifests.sources.destinations", base.BaseDestination
)
