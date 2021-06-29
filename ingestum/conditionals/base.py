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
from typing_extensions import Literal

__script__ = os.path.basename(__file__).replace(".py", "")


class WrongTransformerDefinition(Exception):
    pass


class BaseConditional(BaseModel):
    """
    Base class to support conditional in transformer

    :param arguments: Arguments for the Conditional
    :type arguments: ArgumentsModel
    :param inputs: Inputs required for the Conditional
    :type inputs: InputsModel

    :raises WrongTransformerDefinition:
    """

    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        pass

    type: Literal[__script__] = __script__

    def __init__(self, **kargs):

        # XXX Make both approaches co-exist
        if "arguments" not in kargs:
            kkargs = {}
            kkargs["arguments"] = self.ArgumentsModel(**kargs)
            kargs = kkargs

        super().__init__(**kargs)

        if (
            not hasattr(self, "arguments")
            or not hasattr(self, "inputs")
            or not hasattr(self, "type")
        ):
            raise WrongTransformerDefinition(
                "Subclasses need to define " "arguments, inputs and type " "members"
            )

    def evaluate(self, **kargs):
        self.InputsModel.validate(kargs)
