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

from pydantic import BaseModel
from typing import Any, Optional

from .. import sources


class BaseDocument(BaseModel):
    """
    Base class to support documents

    Document refers to the intermediary and final state
    of an input source

    Input sources are transformed into documents to which
    one or more transformers can apply

    Schemas are in charge of validating the document
    structure and values

    Attributes
    ----------
    type : str
        Identifier for the document
    title : str
        Human readable title for this document
    content : None
        This is defined by each specific document schema
    """

    type: str = "base"
    title: str = ""
    content: Any
    context: Optional[dict] = {}
    origin: Optional[str] = None
    version: str = "1.0"

    @classmethod
    def new_from(cls, _object, **kargs):
        if "title" in kargs:
            pass
        elif isinstance(_object, sources.Base):
            kargs["title"] = _object.get_metadata().get("title", "")
        elif isinstance(_object, BaseDocument):
            kargs["title"] = _object.title

        if "content" in kargs:
            pass
        elif isinstance(_object, cls) and hasattr(_object, "content"):
            kargs["content"] = copy.deepcopy(_object.content)

        _object_dict = {}
        if isinstance(_object, BaseDocument):
            _object_dict = _object.dict()
        kargs["context"] = {
            **_object_dict.get("context", {}),
            **kargs.get("context", {}),
        }

        if "origin" in kargs:
            pass
        elif isinstance(_object, BaseDocument):
            kargs["origin"] = _object.origin

        return cls(**kargs)
