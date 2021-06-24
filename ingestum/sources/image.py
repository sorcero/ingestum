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


from typing_extensions import Literal

from PIL import Image as PILImage
from PIL.ExifTags import TAGS

from .local import LocalSource


class Source(LocalSource):
    """
    Class to support `Image` input sources, e.g. `PNG`, `JPEG`, and others
    """

    type: Literal["image"] = "image"

    def get_metadata(self):
        """
        :return: Dictionary with the metadata (`EXIF tags
            <https://exiftool.org/TagNames/EXIF.html>`_) associated to this
            image source
        :rtype: dict
        """

        if self._metadata is not None:
            return self._metadata

        self._metadata = {}
        image = PILImage.open(self.path)
        exif = image._getexif()

        if exif is not None:
            for (key, val) in exif.items():
                self._metadata[TAGS.get(key)] = val

        image.close()
        return self._metadata
