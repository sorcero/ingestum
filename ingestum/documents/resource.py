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
from pydantic import BaseModel

from typing import Optional
from typing_extensions import Literal


class PDFContext(BaseModel):
    """
    The PDF context model

    :param left: PDF crop-margin left
    :type left: int
    :param top: PDF crop-margin top
    :type top: int
    :param right: PDF crop-margin right
    :type right: int
    :param bottom: PDF crop-margin bottom
    :type bottom: int
    :param page: PDF page number
    :type page: int
    """

    left: int
    top: int
    right: int
    bottom: int
    page: int


class Document(BaseDocument):
    """
    Class to support non-text PDF extractables (or resources) as documents

    :param type: Identifier for the document
    :type type: str
    :param title: Human readable title for this document
    :type title: str
    :param content: Path to the resource in the filesystem
    :type content: str
    :param context: Free-form dictionary with miscellaneous metadata provided by the transformers
    :type context: Optional[dict]
    :param origin: Document origin
    :type origin: Optional[str]
    :param version: Ingestum version
    :type version: str
    :param source: Resource type (e.g., image, table)
    :type source: str
    :param pdf_context: Dictionary with context info from the original source where
        this resource was extracted from
    :type pdf_context: Optional[PDFContext]
    """

    type: Literal["resource"] = "resource"
    source: str = ""
    content: str = ""
    pdf_context: Optional[PDFContext] = None

    @classmethod
    def new_from(cls, _object, **kargs):
        if "source" in kargs:
            pass
        elif hasattr(_object, "source"):
            kargs["source"] = _object.source

        if "pdf_context" in kargs:
            pass
        elif hasattr(_object, "pdf_context"):
            kargs["pdf_context"] = copy.deepcopy(_object.pdf_context)

        return super().new_from(_object, **kargs)
