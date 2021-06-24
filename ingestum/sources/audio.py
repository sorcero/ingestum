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


from tinytag import TinyTag
from typing_extensions import Literal

from .local import LocalSource


TAGS = [
    "title",
    "artist",
    "duration",
]


class Source(LocalSource):
    """
    Class to support `Audio` input sources.
    """

    type: Literal["audio"] = "audio"

    def get_metadata(self):
        """
        :return: Dictionary with the metadata (`title`, `artist`, `duration`)
            associated to this audio source
        :rtype: dict
        """

        if self._metadata is not None:
            return self._metadata

        self._metadata = {}

        audio = TinyTag.get(self.path)
        for tag in TAGS:
            value = getattr(audio, tag)
            if value:
                self._metadata[tag] = value

        return self._metadata
