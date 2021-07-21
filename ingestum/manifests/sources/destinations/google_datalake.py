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

from .base import BaseDestination
from .. import locations

from google.cloud import storage
from google.oauth2 import credentials

__logger__ = logging.getLogger("sorcero.ingestion.services")


class Destination(BaseDestination):
    type: Literal["google_datalake"] = "google_datalake"

    project: str = Field(
        default_factory=lambda: os.environ.get("INGESTUM_GOOGLE_DATALAKE_PROJECT"),
    )

    bucket: str = Field(
        default_factory=lambda: os.environ.get("INGESTUM_GOOGLE_DATALAKE_BUCKET"),
    )

    prefix: str

    credential: Optional[locations.credentials.OAuth2] = None

    def store(self, document, output_dir, artifacts_dir):
        __logger__.debug(
            "storing",
            extra={
                "props": {
                    "project": self.project,
                    "bucket": self.bucket,
                    "prefix": self.prefix,
                }
            },
        )

        self.documentify(document, output_dir)
        artifact = self.artifactify(output_dir, artifacts_dir)
        path = os.path.join(artifacts_dir, artifact)

        credential = None
        if self.credential:
            credential = credentials.Credentials(self.credential.token)

        client = storage.Client(self.project, credentials=credential)
        bucket = client.bucket(self.bucket)

        prefixed_name = f"{self.prefix}_{artifact}"
        blob = bucket.blob(prefixed_name)
        blob.upload_from_filename(path)

        location = locations.GoogleDatalake(
            project=self.project,
            bucket=self.bucket,
            path=prefixed_name,
            credential=self.credential,
        )

        return location
