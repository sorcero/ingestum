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

from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import Optional, List
from typing_extensions import Literal

from .base import BaseTransformer
from .. import sources
from .. import documents
from ..utils import create_request

__script__ = os.path.basename(__file__).replace(".py", "")

__template__ = """<?xml version="1.0" encoding="utf-8"?>   
<searchRequest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="/searchapi_v1.xsd">
<search>
</search>
</searchRequest>"""  # noqa E501


class Transformer(BaseTransformer):
    """
    Extracts documents from `ProQuest` API and returns a collection of `XML`
    documents for each document.

    :param query: Keywords to look for
    :type query: str

    :param databases: Databases to target
    :type databases: list

    :param articles: Maximum number of results
    :type articles: int
    """

    class ArgumentsModel(BaseModel):
        query: str
        databases: List[str]
        articles: int

    class InputsModel(BaseModel):
        source: sources.ProQuest

    class OutputsModel(BaseModel):
        document: documents.Collection

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def get_document(self, source, origin, content):
        return documents.XML.new_from(source, origin=origin, content=content)

    def extract(self, source):
        contents = []

        xml = BeautifulSoup(__template__, "xml")

        query = xml.new_tag("query")
        query.string = self.arguments.query

        databases = xml.new_tag("databases")
        for database in self.arguments.databases:
            tag = xml.new_tag("database")
            tag.string = database
            databases.insert(0, tag)

        search = xml.find("search")
        search.insert(0, query)
        search.insert(1, databases)

        count = xml.new_tag("count")
        count.string = str(self.arguments.articles)
        xml.search.insert_after(count)

        data = str(xml)
        headers = {
            "Accept": "text/xml; charset=UTF-8",
            "Content-Type": "text/xml",
            "Authorization": source.token,
        }
        request = create_request()
        response = request.post(
            source.endpoint, data=data.encode("utf-8"), headers=headers
        )

        soup = BeautifulSoup(response.text, "xml")
        elements = soup.find_all("field", {"name": "Link"})
        for element in elements:
            response = request.get(element.text, headers=headers)
            contents.append(
                self.get_document(
                    source=source, content=response.text, origin=element.text
                )
            )

        return contents

    def transform(self, source: sources.ProQuest) -> documents.Collection:
        super().transform(source=source)

        content = self.extract(source)

        return documents.Collection.new_from(
            source, content=content, context=self.context(exclude=["query"])
        )
