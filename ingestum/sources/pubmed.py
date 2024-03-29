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

from pydantic import Field
from typing_extensions import Literal

from .base import BaseSource


class Source(BaseSource):
    """
    Class to support `PubMed` input sources

    :param tool: `PubMed` search tool (defaults to environment variable
        ``INGESTUM_PUBMED_TOOL``)
    :type tool: str
    :param email: `PubMed` email ID (defaults to environment variable
        ``INGESTUM_PUBMED_EMAIL``)
    :type email: str
    """

    type: Literal["pubmed"] = "pubmed"

    tool: str = Field(
        default_factory=lambda: os.environ.get("INGESTUM_PUBMED_TOOL"),
    )
    email: str = Field(
        default_factory=lambda: os.environ.get("INGESTUM_PUBMED_EMAIL"),
    )
    api_key: str = Field(
        default_factory=lambda: os.environ.get("INGESTUM_PUBMED_API_KEY"),
    )

    def get_metadata(self):
        return super().get_metadata()
