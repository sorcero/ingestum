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
from .. import credentials

from google.cloud import storage
from google.oauth2 import credentials as google_credentials

__logger__ = logging.getLogger("sorcero.ingestion.services")


class Destination(BaseDestination):
    """
    :param project: Google Datalake project name (defaults to environment
        variable ``INGESTUM_GOOGLE_DATALAKE_PROJECT``)
    :type project: str
    :param bucket: Google Datalake bucket name (defaults to environment
        variable ``INGESTUM_GOOGLE_DATALAKE_BUCKET``)
    :type bucket: str
    :param prefix: Artifact prefix
    :type prefix: str
    :param credential: OAuth2 manifest source credential
    :type credential: Optional[credentials.OAuth2]
    """

    type: Literal["google_datalake"] = "google_datalake"

    project: str = Field(
        default_factory=lambda: os.environ.get("INGESTUM_GOOGLE_DATALAKE_PROJECT")
    )

    bucket: str = Field(
        default_factory=lambda: os.environ.get("INGESTUM_GOOGLE_DATALAKE_BUCKET")
    )

    prefix: str

    credential: Optional[credentials.OAuth2] = None

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

        artifact_zip, document_json = self.dump(document, output_dir, artifacts_dir)

        credential = None
        if self.credential:
            credential = google_credentials.Credentials(self.credential.token)

        client = storage.Client(self.project, credentials=credential)
        bucket = client.bucket(self.bucket)

        # store artifact zip
        if artifact_zip is None:
            artifact_location = None
        else:
            artifact_path = os.path.join(artifacts_dir, artifact_zip)

            prefixed_name = f"{self.prefix}_{artifact_zip}"
            blob = bucket.blob(prefixed_name)
            blob.upload_from_filename(artifact_path)

            artifact_location = locations.GoogleDatalake(
                project=self.project,
                bucket=self.bucket,
                path=prefixed_name,
                credential=self.credential,
            )

        # store document json
        document_path = os.path.join(output_dir, document_json)

        prefixed_name = f"{self.prefix}_{document_json}"
        blob = bucket.blob(prefixed_name)
        blob.upload_from_filename(document_path)

        document_location = locations.GoogleDatalake(
            project=self.project,
            bucket=self.bucket,
            path=prefixed_name,
            credential=self.credential,
        )

        return artifact_location, document_location
