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

import re
import logging
import mimetypes

from typing import Optional, Union
from typing_extensions import Literal
from urllib.parse import urlparse

from .. import credentials
from .base import BaseLocation
from ....utils import find_subclasses, create_request

# XXX fixes missing mimetype
mimetypes.add_type(
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"
)
mimetypes.add_type("audio/wave", ".wav")

__logger__ = logging.getLogger("ingestum")
__credentials__ = tuple(find_subclasses(credentials.Base))


class Location(BaseLocation):
    """
    :param url: URL to manifest source
    :type url: str
    :param credential: Manifest source credential
    :type credential: Optional[Union[__credentials__]]
    """

    type: Literal["remote"] = "remote"

    url: str
    credential: Optional[Union[__credentials__]] = None

    def fetch(self, output_dir, cache_dir=None):
        __logger__.debug("fetching", extra={"props": {"url": self.url}})

        headers = {"User-Agent": "Mozilla/5.0", "Connection": "close"}
        if self.credential is not None and self.credential.type == "headers":
            headers = {**headers, **self.credential.content}

        request = create_request(cache_dir=cache_dir).get(self.url, headers=headers)
        request.raise_for_status()

        extension = None
        content_type = request.headers.get("Content-Type")

        if content_type is not None:
            content_type = content_type.split(";")[0]
            extension = mimetypes.guess_extension(content_type)

        if extension is None:
            parsed = urlparse(self.url)
            pattern = re.compile(r".(\w+)$", re.MULTILINE)
            match = pattern.search(parsed.path)
            extension = f".{match.group(1)}" if match else ".unknown"

        path = os.path.join(output_dir, f"source{extension}")

        __logger__.debug("saving", extra={"props": {"source": path}})
        with open(path, "wb") as file:
            file.write(request.content)

        return path
