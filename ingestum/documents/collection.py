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


from .base import BaseDocument

from typing import List, Union
from typing_extensions import Literal

from ..utils import find_subclasses

__documents__ = tuple(list(find_subclasses(BaseDocument)) + ["Document"])


class Document(BaseDocument):
    """
    Class to support a collection of documents

    :param type: Identifier for the document
    :type type: str
    :param title: Human readable title for this document
    :type title: str
    :param content: A list of documents
    :type content: list
    :param context: Free-form dictionary with miscellaneous metadata provided by the transformers
    :type context: Optional[dict]
    :param origin: Document origin
    :type origin: Optional[str]
    :param version: Ingestum version
    :type version: str
    """

    type: Literal["collection"] = "collection"
    content: List[Union[__documents__]] = []


Document.update_forward_refs()
