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

from .base import BaseDocument
from .resource import PDFContext

from typing import Optional
from typing_extensions import Literal


class Document(BaseDocument):
    """
    Class to support text documents

    :param type: Identifier for the document
    :type type: str
    :param title: Human readable title for this document
    :type title: str
    :param content: The full text content
    :type content: str
    :param context: Free-form dictionary with miscellaneous metadata provided by the transformers
    :type context: Optional[dict]
    :param origin: Document origin
    :type origin: Optional[str]
    :param version: Ingestum version
    :type version: str
    :param pdf_context: Dictionary with context info from the orginal PDF where
        this text was extracted from
    :type pdf_context: Optional[PDFContext]
    """

    type: Literal["text"] = "text"
    content: str = ""
    pdf_context: Optional[PDFContext] = None

    @classmethod
    def new_from(cls, _object, **kargs):
        if "pdf_context" in kargs:
            pass
        elif hasattr(_object, "pdf_context"):
            kargs["pdf_context"] = copy.deepcopy(_object.pdf_context)

        return super().new_from(_object, **kargs)
