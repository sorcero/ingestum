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
from twython import Twython

from .base import BaseSource


# Twitter API credentials loaded from env
credentials = {
    "CONSUMER_KEY": os.environ.get("INGESTUM_TWITTER_CONSUMER_KEY"),
    "CONSUMER_SECRET": os.environ.get("INGESTUM_TWITTER_CONSUMER_SECRET"),
    "ACCESS_TOKEN": os.environ.get("INGESTUM_TWITTER_ACCESS_TOKEN"),
    "ACCESS_SECRET": os.environ.get("INGESTUM_TWITTER_ACCESS_SECRET"),
}


class Source(BaseSource):
    """
    Class to support harvesting twitter feeds
    """

    type: Literal["twitter"] = "twitter"

    class Config:
        extra = "allow"

    def __init__(self, **kargs):
        super().__init__(**kargs)
        self._feed = Twython(
            credentials["CONSUMER_KEY"], credentials["CONSUMER_SECRET"]
        )

    def get_feed(self):
        return self._feed
