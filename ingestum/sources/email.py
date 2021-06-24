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


import os

from pydantic import Field
from typing_extensions import Literal

from .base import BaseSource


class Source(BaseSource):
    """
    Class to support `Email` input sources

    :param host: Email host address (defaults to environment variable
        ``INGESTUM_EMAIL_HOST``)
    :type host: str
    :param port: Port number of email host (defaults to environment variable
        ``INGESTUM_EMAIL_PORT``)
    :type port: int
    :param user: Username (defaults to environment variable
        ``INGESTUM_EMAIL_USER``)
    :type user: str
    :param password: User's password (defaults to environment variable
        ``INGESTUM_EMAIL_PASSWORD``)
    :type password: str
    """

    type: Literal["email"] = "email"

    host: str = Field(default_factory=lambda: os.environ.get("INGESTUM_EMAIL_HOST"))
    port: int = Field(default_factory=lambda: os.environ.get("INGESTUM_EMAIL_PORT"))
    user: str = Field(default_factory=lambda: os.environ.get("INGESTUM_EMAIL_USER"))
    password: str = Field(
        default_factory=lambda: os.environ.get("INGESTUM_EMAIL_PASSWORD")
    )

    def get_metadata(self):
        return super().get_metadata()
