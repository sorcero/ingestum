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

from typing_extensions import Literal
from praw import Reddit

from .base import BaseSource


# Reddit API credentials loaded from env
credentials = {
    "CLIENT_ID": os.environ.get("INGESTUM_REDDIT_CLIENT_ID"),
    "CLIENT_SECRET": os.environ.get("INGESTUM_REDDIT_CLIENT_SECRET"),
    "USER_AGENT": "ingestum/0.0.1",
}


class Source(BaseSource):
    """
    Class to support harvesting Reddit sumbissions
    """

    type: Literal["reddit"] = "reddit"

    class Config:
        extra = "allow"

    def __init__(self, **kargs):
        super().__init__(**kargs)
        self._reddit = Reddit(
            client_id=credentials["CLIENT_ID"],
            client_secret=credentials["CLIENT_SECRET"],
            user_agent=credentials["USER_AGENT"],
        )

    def get_reddit(self):
        return self._reddit
