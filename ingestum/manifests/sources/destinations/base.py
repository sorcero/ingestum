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
import json
import uuid
import shutil
import logging

from pydantic import BaseModel
from typing_extensions import Literal

__logger__ = logging.getLogger("sorcero.ingestion.services")

DEFAULT_DOC = "document.json"


class BaseDestination(BaseModel):

    type: Literal["base"] = "base"

    def artifactify(self, output_dir, artifacts_dir):
        name = str(uuid.uuid4())
        zip_path = os.path.join(artifacts_dir, name)
        shutil.make_archive(zip_path, "zip", output_dir)

        return f"{name}.zip"

    def documentify(self, document, output_dir):
        document_path = os.path.join(output_dir, DEFAULT_DOC)
        with open(document_path, "w") as document_file:
            document_file.write(json.dumps(document.dict(), indent=4, sort_keys=True))

    def store(self, document, output_dir, artifacts_dir):
        raise NotImplementedError
