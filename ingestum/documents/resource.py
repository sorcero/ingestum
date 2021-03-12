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
    left: int
    top: int
    right: int
    bottom: int
    page: int


class Document(BaseDocument):
    """
    Class to support external resources as documents

    Attributes
    ----------
    content : str
        Path to the resource in the filesystem
    pdf_context : dict
        Dictionary with context info from the original PDF
        where this table was extracted from
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
