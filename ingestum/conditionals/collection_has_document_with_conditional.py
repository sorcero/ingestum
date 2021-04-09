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

from pydantic import BaseModel
from typing import Optional, Union
from typing_extensions import Literal

from .. import documents
from .base import BaseConditional

__script__ = os.path.basename(__file__).replace(".py", "")
__conditionals__ = tuple(BaseConditional.__subclasses__() + ["Conditional"])


class Conditional(BaseConditional):
    """
    Does this collection includes a document that
    matches the given conditional?

    Parameters
    ----------
    conditional : Conditional
        The conditional to apply to every document
    """

    class ArgumentsModel(BaseModel):
        conditional: Union[__conditionals__]

    class InputsModel(BaseModel):
        document: documents.Collection

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]

    def evaluate(self, document):
        super().evaluate(document=document)

        for _document in document.content:
            if self.arguments.conditional.evaluate(_document) is True:
                return True

        return False


Conditional.ArgumentsModel.update_forward_refs()
Conditional.update_forward_refs()
