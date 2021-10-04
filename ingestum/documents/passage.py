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


import copy

from .text import Document as TextDocument
from pydantic import BaseModel
from typing import Optional, List
from typing_extensions import Literal


class Metadata(BaseModel):
    """
    The metadata model

    :param sha256: SHA256 digest of the content
    :type sha256: str
    :param tags: Strings to associate with the passage, e.g. feature tags (as
        opposed to the style tags expressed in the types field)
    :type tags: List[str]
    :param anchors: e.g. ``<a>`` equivalents in HTML
    :type anchors: List[str]
    :param types: e.g. ``H1``, ``H2``, ``P``, etc.
    :type types: Optional[List[str]]
    """

    sha256: str
    tags: List[str]
    anchors: List[str]
    types: Optional[List[str]] = []


class Document(TextDocument):
    """
    Class to support passsage documents

    :param type: Identifier for the document
    :type type: str
    :param title: Human readable title for this document
    :type title: str
    :param content: The text content
    :type content: str
    :param context: Free-form dictionary with miscellaneous metadata provided by the transformers
    :type context: Optional[dict]
    :param origin: Document origin
    :type origin: Optional[str]
    :param version: Ingestum version
    :type version: str
    :param metadata: The metadata
    :type metadata: Optional[Metadata]
    """

    type: Literal["passage"] = "passage"
    content: str = ""
    metadata: Optional[Metadata] = None

    @classmethod
    def new_from(cls, _object, **kargs):
        if "metadata" in kargs:
            pass
        elif hasattr(_object, "metadata"):
            kargs["metadata"] = copy.deepcopy(_object.metadata)

        return super().new_from(_object, **kargs)
