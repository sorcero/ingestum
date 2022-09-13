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
import mimetypes

from pydantic import Field
from typing import Optional
from typing_extensions import Literal

from google.cloud import storage
from google.oauth2 import credentials as google_credentials

from .. import credentials
from .base import BaseLocation

__logger__ = logging.getLogger("ingestum")


class Location(BaseLocation):
    """
    :param project: Google Datalake project name (defaults to environment
        variable ``INGESTUM_GOOGLE_DATALAKE_PROJECT``)
    :type project: str
    :param bucket: Google Datalake bucket name (defaults to environment
        variable ``INGESTUM_GOOGLE_DATALAKE_BUCKET``)
    :type bucket: str
    :param path: Path to location in Google Datalake
    :type path: str
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

    path: str

    credential: Optional[credentials.OAuth2] = None

    @property
    def uri(self):
        return f"gs://{os.path.join(self.bucket, self.path)}"

    def fetch(self, output_dir, cache_dir=None):
        __logger__.debug(
            "fetching",
            extra={
                "props": {
                    "project": self.project,
                    "bucket": self.bucket,
                    "path": self.path,
                }
            },
        )

        credential = (
            google_credentials.Credentials(self.credential.token)
            if self.credential
            else None
        )
        client = storage.Client(self.project, credentials=credential)
        bucket = client.bucket(self.bucket)

        blob = bucket.blob(self.path)

        if blob.content_type:
            extension = mimetypes.guess_extension(blob.content_type)
        else:
            name, extension = os.path.splitext(self.path)

        path = os.path.join(output_dir, f"source{extension}")

        __logger__.debug("saving", extra={"props": {"source": path}})
        blob.download_to_filename(path)

        return path
