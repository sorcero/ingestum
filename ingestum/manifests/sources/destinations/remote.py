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
import logging

from typing import Optional
from typing_extensions import Literal
from pydantic import Field
from urllib.parse import urlparse

from .base import BaseDestination
from .. import locations
from .... import utils

__logger__ = logging.getLogger("sorcero.ingestion.services")


class Destination(BaseDestination):
    type: Literal["remote"] = "remote"

    url: str = Field(
        default_factory=lambda: os.environ.get("INGESTUM_ARTIFACTS_ENDPOINT"),
    )
    credential: Optional[locations.credentials.Headers] = None

    def store(self, document, output_dir, artifacts_dir):
        __logger__.debug("storing", extra={"props": {"artifacts": self.url}})

        self.documentify(document, output_dir)
        artifact = self.artifactify(output_dir, artifacts_dir)
        path = os.path.join(artifacts_dir, artifact)

        files = []
        files.append(("files", (artifact, open(path, "rb"), "application/zip")))

        headers = self.credential.content if self.credential else {}
        request = utils.create_request().post(
            url=self.url, files=tuple(files), headers=headers
        )
        request.raise_for_status()

        url = urlparse(self.url)
        url = url._replace(path=os.path.join(url.path, artifact[:-4]))
        location = locations.Remote(url=url.geturl(), credential=self.credential)

        return location
