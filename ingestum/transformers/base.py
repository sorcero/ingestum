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
import logging
import datetime

from pydantic import BaseModel
from typing_extensions import Literal

__logger__ = logging.getLogger("ingestum")
__script__ = os.path.basename(__file__).replace(".py", "")


class WrongTransformerInput(Exception):
    pass


class WrongTransformerDefinition(Exception):
    pass


class BaseTransformer(BaseModel):
    class Config:
        extra = "allow"

    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        pass

    class OutputsModel(BaseModel):
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
            or not hasattr(self, "outputs")
            or not hasattr(self, "type")
        ):
            raise WrongTransformerDefinition(
                "Subclasses need to define "
                "arguments, inputs, outputs and type "
                "members"
            )

        if not isinstance(self.arguments, BaseModel):
            raise WrongTransformerDefinition("arguments should be a BaseModel")

        if self.inputs is not None or self.outputs is not None:
            raise WrongTransformerDefinition(
                "inputs and outputs members " "should be Optional"
            )

    """
    Base class to support document transformations

    A transformer represents a single transformation function
    that applies to the document content or its metadata

    As a result, another document is generated. The resulting
    document schema can differ from the original document
    """

    def transform(self, **kargs):
        __logger__.debug("transforming", extra={"props": {"transformer": self.type}})
        self.InputsModel.validate(kargs)

    def context(self):
        return {
            f"{self.type}": {
                **self.arguments.dict(),
                **{"timestamp": datetime.datetime.utcnow().isoformat()},
            }
        }
