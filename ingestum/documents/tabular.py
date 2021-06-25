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

from typing import List, Optional
from typing_extensions import Literal

from .base import BaseDocument
from .resource import PDFContext


class Document(BaseDocument):
    """
    Class to support tabular documents

    :param columns: Number of columns
    :type columns: int
    :param rows: Number of rows
    :type rows: int
    :param content: Table with rows and columns
    :type content: list
    :param pdf_context: Dictionary with context info from the orginal PDF where
        this table was extracted from
    :type pdf_context: Optional[PDFContext]
    """

    type: Literal["tabular"] = "tabular"
    columns: int = 0
    rows: int = 0
    content: List[List[str]] = []
    pdf_context: Optional[PDFContext] = None

    @classmethod
    def new_from(cls, _object, **kargs):
        if "rows" in kargs:
            pass
        elif hasattr(_object, "rows"):
            kargs["rows"] = _object.rows

        if "columns" in kargs:
            pass
        elif hasattr(_object, "columns"):
            kargs["columns"] = _object.columns

        if "pdf_context" in kargs:
            pass
        elif hasattr(_object, "pdf_context"):
            kargs["pdf_context"] = copy.deepcopy(_object.pdf_context)

        return super().new_from(_object, **kargs)
