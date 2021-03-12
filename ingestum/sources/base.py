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


from pydantic import BaseModel
from typing_extensions import Literal


class BaseSource(BaseModel):
    """
    Base class to support input sources

    An input source refers to any file that can be
    ingested, e.g. Text, PDF, HTML or Image files

    This is the abstraction layer needed between
    the ingestion pipeline and real file objects
    """

    class Config:
        extra = "allow"

    type: Literal["base"] = "base"

    def __init__(self, **kargs):
        super().__init__(**kargs)
        self._metadata = None

    def get_metadata(self):
        """
        Returns
        -------
        metadata : dict
            Dictionary with the metadata associated to this input source
        """
        return {}
