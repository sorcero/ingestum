# -*- coding: utf-8 -*-

#
# Copyright (c) 2021 Sorcero, Inc.
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
import uuid
import subprocess

from shutil import which
from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import sources
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")

LIBREOFFICE_BIN = "libreoffice"


class Transformer(BaseTransformer):
    """
    Transforms a `XLS` source into a `Image` Source.
    """

    class ArgumentsModel(BaseModel):
        directory: str
        output: Optional[str] = None

    class InputsModel(BaseModel):
        source: sources.XLS

    class OutputsModel(BaseModel):
        document: sources.Image

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def convert(self, source):
        devnull = open(os.devnull, "w")
        subprocess.call(
            [
                LIBREOFFICE_BIN,
                "--headless",
                "--calc",
                "--convert-to",
                "png:calc_png_Export",
                "--outdir",
                self.arguments.directory,
                source.path,
            ],
            stdout=devnull,
            stderr=subprocess.STDOUT,
        )

        devnull.close()
        name = os.path.basename(source.path)
        name, dot, extension = name.rpartition(".")

        if self.arguments.output is None:
            png_name = f"{str(uuid.uuid4())}.png"
        else:
            png_name = self.arguments.output

        old_path = os.path.join(self.arguments.directory, f"{name}.png")
        new_path = os.path.join(self.arguments.directory, png_name)
        os.rename(old_path, new_path)

        return sources.Image(path=new_path)

    def transform(self, source: sources.XLS) -> sources.Image:
        super().transform(source=source)

        if which(LIBREOFFICE_BIN) is None:
            raise RuntimeError(f"{LIBREOFFICE_BIN} is not installed")

        return self.convert(source)
