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
import json
import hashlib

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from .base import BaseTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a `Collection` of `Passage` documents to a text file.

    :param directory: Path to the directory to store the text file
    :type directory: str
    :param output: File name for the output file
    :type output: str
    """

    class ArgumentsModel(BaseModel):
        directory: str
        output: str

    class InputsModel(BaseModel):
        document: documents.Base

    class OutputsModel(BaseModel):
        document: documents.Base

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def preprocess_images(self):
        table = {}

        for name in os.listdir(self.arguments.directory):
            extension = name.split(".")[-1]
            if extension not in ["png", "jpg", "bmp", "img"]:
                continue

            # dump image to memory
            path = os.path.join(self.arguments.directory, name)
            with open(path, "rb") as image:
                value = image.read()
                key = hashlib.sha256(value).hexdigest()

            # remove original image
            os.remove(path)

            # dump to unique image
            unique = "{}.{}".format(key, extension)
            path = os.path.join(self.arguments.directory, unique)
            if not os.path.exists(path):
                with open(path, "wb") as image:
                    image.write(value)

            # keep track of replacments
            table[name] = unique

        return table

    def preprocess_document(self, document):
        document = json.dumps(
            document.dict(), indent=4, sort_keys=True, ensure_ascii=False
        )

        replace = "[file:///%s]"
        table = self.preprocess_images()
        for name, unique in table.items():
            document = document.replace(replace % name, replace % unique)

        return document

    def extract(self, document):
        document = self.preprocess_document(document)
        path = os.path.join(self.arguments.directory, self.arguments.output)
        with open(path, "w") as file:
            file.write(document)
        return document

    def transform(self, document: documents.Base) -> documents.Base:
        super().transform(document=document)

        if not os.path.exists(self.arguments.directory):
            os.makedirs(self.arguments.directory)

        retval = self.extract(document)

        return documents.Collection.parse_raw(retval)
