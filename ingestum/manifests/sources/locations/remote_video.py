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
import youtube_dl

from typing_extensions import Literal

from .base import BaseLocation

__logger__ = logging.getLogger("ingestum")


class Location(BaseLocation):
    """
    :param url: URL to video
    :type url: str
    """

    type: Literal["remote_video"] = "remote_video"

    url: str

    @property
    def uri(self):
        return self.url

    def fetch(self, output_dir, cache_dir=None):
        __logger__.debug("fetching", extra={"props": {"url": self.url}})

        # we can't specify extension yet due to youtube-dl quirk
        # and we can't store this on /tmp due to xattr limitations
        path = os.path.join(output_dir, "raw")

        options = {
            "format": "bestaudio",
            "outtmpl": f"{path}.%(ext)s",
            "verbose": True,
            "postprocessors": [
                {"key": "MetadataFromTitle", "titleformat": "%(title)s"},
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "0",
                },
                {"key": "XAttrMetadata"},
            ],
        }

        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([self.url])

        # add missing extension
        return f"{path}.wav"
