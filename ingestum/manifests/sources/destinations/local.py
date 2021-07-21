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

import os
import shutil
import logging

from pathlib import Path
from typing_extensions import Literal
from pydantic import Field

from .base import BaseDestination
from .. import locations

__logger__ = logging.getLogger("sorcero.ingestion.services")


class Destination(BaseDestination):
    type: Literal["local"] = "local"

    directory: str = Field(
        default_factory=lambda: os.environ.get("INGESTUM_ARTIFACTS_DIR"),
    )

    def store(self, document, output_dir, artifacts_dir):
        __logger__.debug("storing", extra={"props": {"artifacts": self.directory}})

        Path(self.directory).mkdir(parents=True, exist_ok=True)

        self.documentify(document, output_dir)
        artifact = self.artifactify(output_dir, artifacts_dir)

        source = os.path.join(artifacts_dir, artifact)
        destination = os.path.join(self.directory, artifact)
        shutil.copy(source, destination)

        location = locations.Local(path=destination)

        return location
