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

from .email_source_create_text_collection_document import (
    Transformer as TTransformer,
)  # noqa: E501

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(TTransformer):
    """
    Extracts emails received in the last hours from sender
    and returns a collection of HTML documents for each
    email.

    Parameters
    ----------
    hours : int
        Hours to look back
    sender: str
        Sender email
    subject: str
        Keywords in subject
    body: str
        Keywords in body
    """

    type: Literal[__script__] = __script__

    def extract(self, source, content_type="text/html"):
        return super().extract(source, content_type)
