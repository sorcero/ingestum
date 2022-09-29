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
import uuid
import shutil
import logging

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from ingestum.utils import write_document_to_path

__logger__ = logging.getLogger("sorcero.ingestion.services")

DEFAULT_DOC = "document.json"


class BaseDestination(BaseModel):

    type: Literal["base"] = "base"

    exclude_artifact: Optional[bool] = False

    def _generate_unique_name(self):
        return str(uuid.uuid4())

    def _artifactify(self, document, name, output_dir, artifacts_dir):
        if self.exclude_artifact is True:
            return None

        document_path = os.path.join(output_dir, DEFAULT_DOC)
        write_document_to_path(document, document_path, formatted=False)

        zip_path = os.path.join(artifacts_dir, name)
        shutil.make_archive(zip_path, "zip", output_dir)

        return f"{name}.zip"

    def _documentify(self, document, name, output_dir):
        name = f"{name}.json"
        document_path = os.path.join(output_dir, name)
        write_document_to_path(document, document_path, formatted=False)

        return name

    def dump(self, document, output_dir, artifacts_dir):
        name = self._generate_unique_name()

        # note that order matter here
        artifact_zip = self._artifactify(document, name, output_dir, artifacts_dir)
        document_json = self._documentify(document, name, output_dir)

        return artifact_zip, document_json

    def store(self, document, output_dir, artifacts_dir):
        raise NotImplementedError
