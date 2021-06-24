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
from praw import Reddit

from .base import BaseSource


class Source(BaseSource):
    """
    Class to support harvesting `Reddit` sumbissions.

    :param client_id: Reddit app API `Client ID` (`required`, defaults to
        environment variable ``INGESTUM_REDDIT_CLIENT_ID``)
    :type client_id: str
    :param client_secret: Reddit app API `Client Secret` (`required`, defaults
        to environment variable ``INGESTUM_REDDIT_CLIENT_SECRET``)
    :type client_secret: str
    :param user_agent: Reddit app API `User Agent` (`required`, defaults to
        ``"ingestum/0.0.1"``)
    """

    type: Literal["reddit"] = "reddit"

    client_id: str = Field(
        default_factory=lambda: os.environ.get("INGESTUM_REDDIT_CLIENT_ID"),
    )
    client_secret: str = Field(
        default_factory=lambda: os.environ.get("INGESTUM_REDDIT_CLIENT_SECRET"),
    )
    user_agent: str = Field(
        default_factory=lambda: "ingestum/0.0.1",
    )

    def __init__(self, **kargs):
        super().__init__(**kargs)
        self._reddit = Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
        )

    def get_reddit(self):
        return self._reddit

    def get_metadata(self):
        return super().get_metadata()
