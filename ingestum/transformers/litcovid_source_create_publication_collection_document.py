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
import asyncio
import time

from typing import Optional
from typing_extensions import Literal
from pyppeteer import launch
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urljoin, quote

from .. import sources
from .. import documents
from .pubmed_source_create_publication_collection_document import (
    Transformer as BaseTransformer,
)


LITCOVID_BASE_URL = "https://www.ncbi.nlm.nih.gov/"
LITCOVID_SEARCH_ENDPOINT = "https://www.ncbi.nlm.nih.gov/research/coronavirus/docsum"

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Extracts documents from `LitCovid` API and returns a collection of `Publication`
    documents for each article, with additional information extracted from `PubMed`.

    :param terms: PubMed queries
    :type terms: list
    :param articles: The number of publications to retrieve
    :type articles: int
    :param hours: Hours to look back from now
    :type hours: int
    :param from_date: Lower entrez date range limit
    :type from_date: str
    :param to_date: Upper entrez date range limit
    :type to_date: str
    :param query_string: Pre-formatted query string
    :type query_string: str
    :param sort: The sorting criteria for the search
        The options are: ``"_id desc"``, ``"score desc"``, ``"date desc"``; defaults to ``"score desc"``
    :type sort: Optional[str]
    """

    class ArgumentsModel(BaseTransformer.ArgumentsModel):
        query_string: str
        sort: Optional[str] = "score desc"

    class InputsModel(BaseTransformer.InputsModel):
        source: sources.LitCovid

    class OutputsModel(BaseTransformer.OutputsModel):
        document: documents.Collection

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    async def get_page_body_html(self, page_no):
        # Create a browser and navigate to query
        browser = await launch()
        page = await browser.newPage()

        # The query format is described here:
        # https://www.ncbi.nlm.nih.gov/research/coronavirus/faq#:~:text=What%20types%20of%20searches%20are%20supported%20in%20LitCovid%3F

        query = {
            "text": self.arguments.query_string,
            "sort": self.arguments.sort,
            "page": page_no,
        }

        url = urljoin(LITCOVID_SEARCH_ENDPOINT, f"?{urlencode(query, quote_via=quote)}")
        await page.goto(f"{url}", options={"waitUntil": "networkidle0"})

        element = await page.querySelector("body")
        body = await page.evaluate("(element) => element.innerHTML", element)

        await browser.close()
        return BeautifulSoup(str(body), "lxml")

    def extract_from_litcovid(self):
        soup = asyncio.get_event_loop().run_until_complete(self.get_page_body_html(1))
        max_page = soup.find("div", "pagination-wrapper")
        if max_page is None:
            return []
        max_page_no = int(max_page.text.split(" ")[4])

        page_no = 0
        publication_count = 0
        publications = {}
        while publication_count < self.arguments.articles and page_no < max_page_no:
            page_no += 1
            time.sleep(0.33)
            soup = asyncio.get_event_loop().run_until_complete(
                self.get_page_body_html(page_no)
            )
            page_publications = soup.findAll("div", "publication")

            for i in range(
                min(len(page_publications), self.arguments.articles - publication_count)
            ):
                publication_count += 1

                relative_origin = page_publications[i].find("a", "publication-title")[
                    "href"
                ]
                countries = page_publications[i].find("div", "tags countries")
                countries_list = (
                    countries.findAll("div", "tag") if countries is not None else []
                )
                topics = page_publications[i].find("div", "tags topics")
                topics_list = topics.findAll("div", "tag") if topics is not None else []
                pmid = relative_origin.split("/")[-1]

                publications[pmid] = {
                    "origin": urljoin(LITCOVID_BASE_URL, relative_origin),
                    "countries": sorted([country.text for country in countries_list]),
                    "topics": sorted([topic.text for topic in topics_list]),
                }

        return publications

    def get_document(self, source, origin, content):
        document = super().get_document(source=source, origin=origin, content=content)

        res_soup = BeautifulSoup(str(content), "xml")
        res_PMID = res_soup.find("PMID")
        pmid = res_PMID.text if res_PMID is not None else ""

        document.context[self.type] = {}
        document.context[self.type]["pmid"] = pmid
        document.context[self.type]["countries"] = (
            self._publications[pmid]["countries"] if pmid != "" else ""
        )
        document.context[self.type]["topics"] = (
            self._publications[pmid]["topics"] if pmid != "" else ""
        )
        return document

    def extract(self, source):
        self._publications = self.extract_from_litcovid()

        if len(self._publications) == 0:
            return []

        appended_query = f" AND ({' OR '.join([key + '[PMID]' for key in self._publications.keys()])})"
        for index, term in enumerate(self.arguments.terms):
            self.arguments.terms[index] = term + appended_query

        return super().extract(source)

    # redundantly added for auto documentation
    def transform(self, source: sources.LitCovid) -> documents.Collection:
        return super().transform(source=source)
