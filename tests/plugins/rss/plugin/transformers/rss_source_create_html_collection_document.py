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
import requests

from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from ingestum import documents
from ingestum import sources
from ingestum import transformers

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(transformers.base.BaseTransformer):
    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        source: sources.RSS

    class OutputsModel(BaseModel):
        document: documents.Collection

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    """
    Transforms a RSS feed into a collection of HTML documents.
    """

    def extract(self, source):
        contents = []

        response = requests.get(source.url)

        soup = BeautifulSoup(response.text, "xml")
        elements = soup.find_all("link")
        for element in elements:
            if not element.text:
                continue
            response = requests.get(element.text)
            contents.append(documents.HTML.new_from(None, content=response.text))

        return contents

    def transform(self, source):
        super().transform(source=source)

        content = self.extract(source)

        return documents.Collection.new_from(None, content=content)
