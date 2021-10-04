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
from .. import credentials
from .... import utils

__logger__ = logging.getLogger("sorcero.ingestion.services")


class Destination(BaseDestination):
    """
    :param url: Artifact endpoint (defaults to environment
        variable ``INGESTUM_ARTIFACTS_ENDPOINT``)
    :type url: str
    :param credential: Credential headers
    :type credential: Optional[credentials.Headers]
    """

    type: Literal["remote"] = "remote"

    url: str = Field(
        default_factory=lambda: os.environ.get("INGESTUM_ARTIFACTS_ENDPOINT")
    )
    credential: Optional[credentials.Headers] = None

    def store(self, document, output_dir, artifacts_dir):
        __logger__.debug("storing", extra={"props": {"artifacts": self.url}})

        artifact_zip, document_json = self.dump(document, output_dir, artifacts_dir)

        # upload artifact zip and document json
        artifact_path = os.path.join(artifacts_dir, artifact_zip)
        document_path = os.path.join(output_dir, document_json)

        files = []
        files.append(
            ("files", (artifact_zip, open(artifact_path, "rb"), "application/zip"))
        )
        files.append(
            ("files", (document_json, open(document_path, "rb"), "application/json"))
        )

        headers = self.credential.content if self.credential else {}
        request = utils.create_request().post(
            url=self.url, files=tuple(files), headers=headers
        )
        request.raise_for_status()

        # craft locations for both
        url = urlparse(self.url)
        artifact_url = url._replace(path=os.path.join(url.path, artifact_zip))
        document_url = url._replace(path=os.path.join(url.path, document_json))

        artifact_location = locations.Remote(
            url=artifact_url.geturl(), credential=self.credential
        )
        document_location = locations.Remote(
            url=document_url.geturl(), credential=self.credential
        )

        return artifact_location, document_location
