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
import time
import logging
import requests
import datetime

from urllib.parse import urlencode, urljoin
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import Optional, List
from typing_extensions import Literal

from .base import BaseTransformer
from .. import sources
from .. import documents

__script__ = os.path.basename(__file__).replace(".py", "")
__logger__ = logging.getLogger("ingestum")

PUBMED_ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
PUBMED_ESEARCH = "esearch.fcgi"
PUBMED_EFETCH = "efetch.fcgi"
PUBMED_DB = "pubmed"
PUBMED_TYPE = "medline"
PUBMED_RETMODE = "text"
PUBMED_DELAY = 0.333
PUBMED_ERROR = "Error occurred"
PUBMED_MAX_RETRIES = 10


class Transformer(BaseTransformer):
    """
    Extracts documents from PubMed API and returns a
    collection of TEXT documents for each article.

    Parameters
    ----------
    terms : list
        Keywords to look for
    articles: int
        The number of articles to retrieve
    hours: int
        Hours to look back from now
    """

    class ArgumentsModel(BaseModel):
        terms: List[str]
        articles: int
        hours: int

    class InputsModel(BaseModel):
        source: sources.PubMed

    class OutputsModel(BaseModel):
        document: documents.Collection

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def fetch_article(self, source, id):
        query = {
            "tool": source.tool,
            "email": source.email,
            "id": id,
            "db": PUBMED_DB,
            "rettype": PUBMED_TYPE,
            "retmode": PUBMED_RETMODE,
        }

        url = urljoin(f"{PUBMED_ENDPOINT}/{PUBMED_EFETCH}", f"?{urlencode(query)}")
        sleep = PUBMED_DELAY

        for retry in range(PUBMED_MAX_RETRIES):
            # respect pubmed wishes
            time.sleep(sleep)

            response = requests.get(url)
            if not PUBMED_ERROR in response.text:
                return url, response.text

            sleep += PUBMED_DELAY
            __logger__.debug(
                "(%d/%d) failed to download %s retry in %f"
                % (retry + 1, PUBMED_MAX_RETRIES, url, sleep)
            )

        return None, None

    def fetch_search(self, source):
        delta = datetime.timedelta(hours=self.arguments.hours)
        end = datetime.datetime.now()
        start = end - delta

        terms = "OR".join(
            [f"({term.replace(' ', '+')})" for term in self.arguments.terms]
        )
        terms += f'(("{start.isoformat()}"[Date - Publication] : "3000"[Date - Publication]))'

        query = {
            "tool": source.tool,
            "email": source.email,
            "db": PUBMED_DB,
            "retmax": self.arguments.articles,
            "term": terms,
        }
        url = urljoin(f"{PUBMED_ENDPOINT}/{PUBMED_ESEARCH}", f"?{urlencode(query)}")
        response = requests.get(url)

        return response.text

    def extract(self, source):
        contents = []

        results = self.fetch_search(source)
        soup = BeautifulSoup(results, "xml")
        elements = soup.findAll("Id")
        for element in elements:
            origin, content = self.fetch_article(source, element.text)
            if not content:
                continue

            document = documents.Text.new_from(None, origin=origin, content=content)
            contents.append(document)

        return contents

    def transform(self, source):
        super().transform(source=source)

        content = self.extract(source)

        return documents.Collection.new_from(
            source,
            content=content,
            context=self.context(),
        )
