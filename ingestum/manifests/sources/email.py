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

from ... import sources
from .base import BaseSource


class Source(BaseSource):
    """
    :param hours: Hours to look back
    :type hours: int
    :param sender: Sender of email
    :type sender: str
    :param subject: Keywords in subject
    :type subject: str
    :param body: Keywords in body
    :type body: str
    """

    type: Literal["email"] = "email"

    hours: int
    hours_placeholder = -1

    sender: str
    sender_placeholder = ""

    subject: str
    subject_placeholder = ""

    body: str
    body_placeholder = ""

    def get_source(self, output_dir, cache_dir):
        return sources.Email(context=self.context)
