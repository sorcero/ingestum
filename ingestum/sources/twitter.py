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
from twython import Twython

from .base import BaseSource


# Twitter API credentials loaded from env
# credentials = {
#     "CONSUMER_KEY": os.environ.get("INGESTUM_TWITTER_CONSUMER_KEY"),
#     "CONSUMER_SECRET": os.environ.get("INGESTUM_TWITTER_CONSUMER_SECRET"),
#     "ACCESS_TOKEN": os.environ.get("INGESTUM_TWITTER_ACCESS_TOKEN"),
#     "ACCESS_SECRET": os.environ.get("INGESTUM_TWITTER_ACCESS_SECRET"),
# }


class Source(BaseSource):
    """
    Class to support harvesting `Twitter` feeds

    :param consumer_key: Twitter app API `Consumer Key` (defaults to environment
        variable ``INGESTUM_TWITTER_CONSUMER_KEY``)
    :type consumer_key: str
    :param consumer_secret: Twitter app API `Consumer Secret` (defaults to
        environment variable ``INGESTUM_TWITTER_CONSUMER_SECRET``)
    :type consumer_secret: str
    """

    type: Literal["twitter"] = "twitter"

    consumer_key: str = Field(
        default_factory=lambda: os.environ.get("INGESTUM_TWITTER_CONSUMER_KEY")
    )
    consumer_secret: str = Field(
        default_factory=lambda: os.environ.get(
            "INGESTUM_TWITTER_CONSUMER_SECRET"
        )
    )

    def __init__(self, **kargs):
        super().__init__(**kargs)
        self._feed = Twython(self.consumer_key, self.consumer_secret)

    def get_feed(self):
        return self._feed
    
    def get_metadata(self):
        return super().get_metadata()
