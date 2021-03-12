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

from .. import documents
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a Passage document into another Passage document with a
    new metadata field added, extracted from the passage attribute.

    Parameters
    ----------
    attribute : str
        Name of the document attribute
    regexp : str
        Regular expression to extract the value out of the attribute
    key: str
        Metadata key where the result will be added
    value : str
        String with value format assuming one %s
    """

    class ArgumentsModel(BaseModel):
        attribute: str
        regexp: str
        key: str
        value: str

    class InputsModel(BaseModel):
        document: documents.Passage

    class OutputsModel(BaseModel):
        document: documents.Passage

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def metadata_with_metadata(self, metadata, values):
        retval = metadata.copy()
        if values is not None:
            value_list = list(
                set.union(set(getattr(retval, self.arguments.key)), set(values))
            )
            value_list.sort()
            setattr(retval, self.arguments.key, value_list)

        return retval

    def extract(self, document):
        pattern = re.compile(self.arguments.regexp, re.MULTILINE)

        if not hasattr(document, self.arguments.attribute):
            return None

        matches = pattern.findall(getattr(document, self.arguments.attribute))
        return [
            self.arguments.value % (match[0] if isinstance(match, tuple) else match)
            for match in matches
        ]

    def transform(self, document):
        super().transform(document=document)

        values = self.extract(document)
        metadata = self.metadata_with_metadata(document.metadata, values)

        return document.new_from(document, metadata=metadata)
