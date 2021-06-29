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
import re

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .base import BaseTransformer
from .. import documents

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a `Text` document with section numbers into another `Text`
    document where a passage identifier is inserted.

    :param regexp: Regular expression to identify the exact place to add the
        marker. Note that the expression must define two groups, for what comes
        before and after the divider, e.g. ``(^)(\\d+)``
    :type regexp: str
    :param marker: String to be added as the marker
    :type marker: str
    """

    class ArgumentsModel(BaseModel):
        regexp: str
        marker: str

    class InputsModel(BaseModel):
        document: documents.Text

    class OutputsModel(BaseModel):
        document: documents.Text

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def add_markers(self, content):
        pattern = re.compile(self.arguments.regexp, re.MULTILINE)
        # note that the marker is added between the 1st and 2nd matching groups
        return re.sub(pattern, r"\1%s\2" % self.arguments.marker, content)

    def transform(self, document: documents.Text) -> documents.Text:
        super().transform(document=document)

        content = self.add_markers(document.content)

        return document.new_from(document, content=content)
