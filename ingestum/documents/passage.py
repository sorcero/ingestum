# -*- coding: utf-8 -*-

#
# Copyright (c) 2020, 2022 Sorcero, Inc.
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


class Font(BaseModel):
    """
    The font model

    :param bold: Bold font
    :type bold: bool
    :param color: Color of the font
    :type color: str
    :param italic: Italic font
    :type italic: bool
    :param name: Name of the font
    :type name: str
    :param size: Size of the font
    :type size: float
    :param underline: Underline font
    :type underline: bool
    :param strike_through: Strike through font
    :type strike_through: bool
    :param all_caps: All caps font
    :type all_caps: bool
    :param weight: Weight of the font
    :type weight: int
    :param monospaced: Monospaced font
    :type monospaced: bool
    """

    bold: bool = None
    color: str = None
    italic: bool = None
    name: str = None
    size: float = None
    underline: bool = None
    strike_through: bool = None
    all_caps: bool = None
    weight: int = None
    monospaced: bool = None


class ListStyling(BaseModel):
    """
    The listStyling model

    :param list_symbol: The list symbol
    :type list_symbol: str
    :param list_id: The list id
    :type list_id: str
    :param list_level: The list indentation level
    :type list_level: int
    :param is_list: Whether or not the text is a list
    :type is_list: bool
    """

    list_symbol: str = None
    list_id: str = None
    list_level: int = None
    is_list: bool = None


class TextStyling(BaseModel):
    """
    The textStyling model.

    :param content: The content to which the styling is applied
    :type content: str
    :param alignment: The alignment of the text
    :type alignment: str
    :param list_styling: The list information
    :type list_styling: ListStyling
    :param font: The font styling of the text
    :type font: List[Font]
    :param indent: The indent of the text
    :type indent: float
    :param spacing: The spacing of the text
    :type spacing: int
    :param name: The style name.
    :type name: str
    :param space_after: The space after the text
    :type space_after: int
    :param line_height: The line height of the text
    :type line_height: float
    """

    content: Optional[str] = None
    alignment: str = None
    list_styling: ListStyling = None
    font: List[Font] = None
    indent: float = None
    spacing: int = None
    name: str = None
    space_after: int = None
    line_height: float = None


class Styling(BaseModel):
    """
    The styling model

    :param type: The type of the styling
    :type type: str
    :param fill_type: The fill type block/shape (solid, gradient, pattern, etc.)
    :type fill_type: str
    :param background_color: The background color of the block/shape
    :type background_color: str
    :param text_styling: The text styling of the block/shape
    :type text_styling: List[TextStyling]
    """

    type: str = None
    fill_type: str = None
    background_color: str = None
    text_styling: List[TextStyling] = None


class Dimensions(BaseModel):
    """
    The dimensions model

    :param height: The height of the shape/block
    :type height: float
    :param width: The width of the shape/block
    :type width: float
    :param top: The space to the top of the page
    :type top: float
    :param left: The space to the left of the page
    :type left: float
    """

    height: float = None
    left: float = None
    top: float = None
    width: float = None


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
    :param styling: The styling associated with the Passage text taken from the original source
    :type styling: Optional[Styling]
    :param dimensions: The dimensions
    :type dimensions: Optional[Dimensions]
    """

    type: Literal["passage"] = "passage"
    content: str = ""
    metadata: Optional[Metadata] = None
    styling: Optional[Styling] = None
    dimensions: Optional[Dimensions] = None

    @classmethod
    def new_from(cls, _object, **kargs):
        if "metadata" in kargs:
            pass
        elif hasattr(_object, "metadata"):
            kargs["metadata"] = copy.deepcopy(_object.metadata)

        if "styling" in kargs:
            pass
        elif hasattr(_object, "styling"):
            kargs["styling"] = copy.deepcopy(_object.styling)

        if "dimensions" in kargs:
            pass
        elif hasattr(_object, "dimensions"):
            kargs["dimensions"] = copy.deepcopy(_object.dimensions)

        return super().new_from(_object, **kargs)
