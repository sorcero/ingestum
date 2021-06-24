# -*- coding: utf-8 -*-

#
# Copyright (c) 2020 Sorcero, Inc.
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


from bs4 import BeautifulSoup
from typing_extensions import Literal

from .local import LocalSource

METADATA = {
    "og:title": "title",
    "og:url": "url",
    "og:description": "description",
    "og:locale": "locale",
    "og:image": "image",
}


class Source(LocalSource):
    """
    Class to support `HTML` input sources
    """

    type: Literal["html"] = "html"

    def get_metadata(self):
        """
        :return: Dictionary with the metadata (`title`, `URL`, `description`,
            `locale`, `image`) associated to this HTML source
        :rtype: dict
        """

        if self._metadata is not None:
            return self._metadata

        self._metadata = {}
        file = open(self.path, "r")
        soup = BeautifulSoup(file.read(), "lxml")

        for tag in soup.find_all("meta"):
            key = tag.get("property", "")
            if key in METADATA:
                value = tag.get("content", "")
                self._metadata[METADATA[key]] = value

        file.close()
        return self._metadata
