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
import re
import logging
import requests
import datetime

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urljoin
from string import whitespace

from .. import documents
from .. import sources
from .. import utils
from .base import BaseTransformer

__logger__ = logging.getLogger("ingestum")
__script__ = os.path.basename(__file__).replace(".py", "")

ENDPOINTS = {
    "EUROPEPMC_SEARCH_ENDPOINT": os.environ.get(
        "INGESTUM_EUROPEPMC_SEARCH_ENDPOINT",
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
    ),
    "EUROPEPMC_ARTICLE_ENDPOINT": os.environ.get(
        "INGESTUM_EUROPEPMC_ARTICLE_ENDPOINT", "https://europepmc.org/article/"
    ),
    "EUROPEPMC_FULL_TEXT_ENDPOINT": os.environ.get(
        "INGESTUM_EUROPEPMC_FULL_TEXT_ENDPOINT",
        "https://www.ebi.ac.uk/europepmc/webservices/rest/",
    ),
}


class Transformer(BaseTransformer):
    """
    Transforms a `Europe PMC` source into a `Collection` of `Publication` documents

    :param query: Europe PMC search query
    :type query: str
    :param articles: The number of publications to retrieve
    :type articles: int
    :param hours: Hours to look back from now
    :type hours: int
    :param from_date: Lower limit for publication date
    :type from_date: str
    :param to_date: Upper limit for publication date
    :type to_date: str
    :param full_text: Extract the full text article if set to True (defaults to False)
    :type full_text: bool
    """

    class ArgumentsModel(BaseModel):
        query: str
        articles: int
        hours: Optional[int] = -1
        from_date: Optional[str] = ""
        to_date: Optional[str] = ""
        full_text: Optional[bool] = False

    class InputsModel(BaseModel):
        source: sources.EuropePMC

    class OutputsModel(BaseModel):
        document: documents.Collection

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def get_abstract(self, res_abstract):
        soup = BeautifulSoup(res_abstract, "html.parser")

        # Format <h4>text</h4> to TEXT:
        for abstract_subtitle in soup.find_all("h4", recursive=False):
            abstract_subtitle_text = abstract_subtitle.text.strip(": ").upper()
            if not abstract_subtitle_text:
                continue
            abstract_subtitle.replace_with(f" {abstract_subtitle_text}: ")

        return soup.text.strip()

    def get_title(self, title_node):
        title = self.remove_xml_tags(title_node.text)
        return title.strip(f"{whitespace}.")

    def remove_xml_tags(self, content):
        return BeautifulSoup(content, "html.parser").text

    def get_start(self):
        delta = datetime.timedelta(hours=self.arguments.hours)
        end = datetime.datetime.now()
        start = end - delta

        return start

    def get_authors(self, author_nodes_list):
        authors = []
        for author_node in author_nodes_list:
            surname = ""
            if surname_node := author_node.find("lastName"):
                surname = utils.sanitize_string(surname_node.text)

            given_names = ""
            if given_names_node := author_node.find("firstName"):
                given_names = utils.sanitize_string(given_names_node.text)

            affiliation_nodes = author_node.find_all("affiliation")
            affiliation = []
            for affiliation_node in affiliation_nodes:
                affiliation.append(utils.sanitize_string(affiliation_node.text))

            authors.append(
                documents.publication.Author(
                    name=f"{surname}, {given_names}", affiliation=affiliation
                )
            )

        return authors

    def get_full_text_url(self, full_text_url_nodes_list):
        if len(full_text_url_nodes_list) == 0:
            return ""

        full_text_url = ""
        for full_text_url_node in full_text_url_nodes_list:
            if full_text_url == "":
                if url_node := full_text_url_node.find("url"):
                    full_text_url = url_node.text
            elif availability := full_text_url_node.find("availability"):
                if availability.text == "Free":
                    if url_node := full_text_url_node.find("url"):
                        full_text_url = url_node.text
        return full_text_url

    def get_keywords(self, keyword_nodes_list):
        keywords = []
        for keyword_node in keyword_nodes_list:
            keywords.append(keyword_node.text)
        return keywords

    def get_publication_type(self, publication_type_nodes_list):
        publication_type = []

        for publication_type_node in publication_type_nodes_list:
            text = publication_type_node.text.strip()

            # Reformat following cases:
            # * abstract -> Abstract
            # * article-commentary -> Article Commentary
            if re.search(r"^([a-z]*)(-([a-z]*))*$", text):
                text = " ".join(map(lambda x: x.capitalize(), text.split("-")))

            publication_type.append(text)

        return publication_type

    def get_provider_url(self, result_node):
        id_node = result_node.find("id")
        source_node = result_node.find("source")
        if source_node and id_node:
            url = urljoin(self.article_endpoint, source_node.text)
            return urljoin(f"{url}/", id_node.text)
        return ""

    def get_origin(self, provider_id):
        parameters = {
            "query": provider_id,
            "resultType": "core",
            "synonym": "FALSE",
            "pageSize": 1,
            "format": "xml",
            "fromSearchPost": "false",
            "cursorMark": "",
        }
        return urljoin(self.search_endpoint, f"?{urlencode(parameters)}")

    def get_full_text(self, provider_id, full_text_id_list_node):
        if full_text_id_list_node is not None:
            for full_text_id_node in full_text_id_list_node.find_all("fullTextId"):
                full_text_url = f"{ENDPOINTS['EUROPEPMC_FULL_TEXT_ENDPOINT']}{full_text_id_node.text}/fullTextXML"
                __logger__.debug(
                    "extracting full text",
                    extra={"props": {"transformer": self.type, "url": full_text_url}},
                )

                full_text = ""
                try:
                    response = requests.get(full_text_url)
                    response.raise_for_status()
                except Exception as e:
                    __logger__.warning(
                        "full text extraction failed",
                        extra={
                            "props": {
                                "transformer": self.type,
                                "url": full_text_url,
                                "error": str(e),
                            }
                        },
                    )
                else:
                    soup = BeautifulSoup(response.content, "lxml")

                    body_node = soup.body
                    for restricted_by_node in body_node.select("restricted-by"):
                        restricted_by_node.extract()
                    for front_node in body_node.select("front"):
                        front_node.extract()
                    for back_node in body_node.select("back"):
                        back_node.extract()
                    full_text = body_node.text

                if full_text != "":
                    return full_text

        __logger__.error(
            "no full text available",
            extra={
                "props": {
                    "transformer": self.type,
                    "provider_id": provider_id,
                }
            },
        )
        return ""

    def get_document(self, result):
        result_dict = {}

        # Get title
        if title_node := result.find("title"):
            result_dict["title"] = self.get_title(title_node)

        # Get abstract
        if abstract_node := result.find("abstractText"):
            result_dict["abstract"] = self.get_abstract(abstract_node.text)

        # Get authors
        result_dict["authors"] = self.get_authors(result.find_all("author"))

        # Get publication date
        if publication_date_node := result.find("firstPublicationDate"):
            result_dict["publication_date"] = publication_date_node.text

        # Get entrez date
        if entrez_date_node := result.find("firstIndexDate"):
            result_dict["entrez_date"] = entrez_date_node.text

        # Get journal, abbreviation and journal ISSN
        if journal_node := result.find("journal"):
            if journal_title_node := journal_node.find("title"):
                result_dict["journal"] = utils.sanitize_string(journal_title_node.text)
            if journal_abbreviation_node := journal_node.find("ISOAbbreviation"):
                result_dict["journal_abbreviation"] = utils.sanitize_string(
                    journal_abbreviation_node.text
                )
            if journal_issn_node := journal_node.find("ISSN"):
                result_dict["journal_ISSN"] = utils.sanitize_string(
                    journal_issn_node.text
                )

        # Fallback to Publisher if Journal is not available
        if not journal_node and (publisher_node := result.find("publisher")):
            result_dict["journal"] = utils.sanitize_string(publisher_node.text)

        # Get journal volume
        if volume_node := result.find("volume"):
            result_dict["journal_volume"] = volume_node.text

        # Get journal issue number
        if issue_node := result.find("issue"):
            result_dict["journal_issue"] = issue_node.text

        # Get provider
        result_dict["provider"] = "europepmc"

        # Get provider id
        if id_node := result.find("id"):
            result_dict["provider_id"] = id_node.text

        # Get provider url
        result_dict["provider_url"] = self.get_provider_url(result)

        # Get pagination info
        if pagination_node := result.find("pageInfo"):
            result_dict["pagination"] = pagination_node.text

        # Get full text
        if self.arguments.full_text:
            result_dict["content"] = self.get_full_text(
                result_dict["provider_id"], result.find("fullTextIdList")
            )

        # Get full text
        result_dict["full_text_url"] = self.get_full_text_url(
            result.find_all("fullTextUrl")
        )

        # Get language
        if language_node := result.find("language"):
            result_dict["language"] = language_node.text

        # Get keywords
        result_dict["keywords"] = self.get_keywords(result.find_all("keyword"))

        # Get origin
        result_dict["origin"] = self.get_origin(result_dict["provider_id"])

        # Get publication type(s)
        result_dict["publication_type"] = self.get_publication_type(
            result.find_all("pubType")
        )

        # Get DOI
        if doi_node := result.find("doi"):
            result_dict["doi"] = doi_node.text

        return documents.Publication.new_from(None, **result_dict)

    def get_documents(self, response):
        publication_documents = []
        soup = BeautifulSoup(str(response), "xml")

        # Get the cursor mark for the next page
        if nextCursorMark := soup.find("nextCursorMark"):
            nextCursorMark = nextCursorMark.text
        else:
            nextCursorMark = None

        # Get all publications
        results_list = soup.find_all("result")

        # Create and pupulate a publication document for each result
        for result in results_list:
            try:
                publication_documents.append(self.get_document(result))
            except Exception as e:
                __logger__.error(
                    "can't parse publication",
                    extra={
                        "props": {
                            "transformer": self.type,
                            "error": str(e),
                        }
                    },
                )
                continue

        return publication_documents, nextCursorMark

    def extract(self):
        self.search_endpoint = ENDPOINTS.get("EUROPEPMC_SEARCH_ENDPOINT")
        self.article_endpoint = ENDPOINTS.get("EUROPEPMC_ARTICLE_ENDPOINT")

        full_query = f"{self.arguments.query}"

        has_hours = self.arguments.hours > 0
        has_from = self.arguments.from_date != ""
        has_to = self.arguments.to_date != ""

        if has_hours and (has_from or has_to):
            logging.warning(
                "Arguments 'hours' and 'from_date/to_date' are mutually exclusive ('hours' will be ignored)"
            )

        if has_from and has_to:
            full_query += f" AND (CREATION_DATE:[{self.arguments.from_date} TO {self.arguments.to_date}])"
        elif has_from:
            full_query += (
                f" AND (CREATION_DATE:[{self.arguments.from_date} TO 3000-12-31])"
            )
        elif has_to:
            full_query += (
                f" AND (CREATION_DATE:[1900-01-01 TO {self.arguments.to_date}])"
            )
        elif has_hours:
            start = self.get_start()
            publication_date = "%d-%02d-%d" % (start.year, start.month, start.day)
            full_query += f" AND (CREATION_DATE:[{publication_date} TO 3000-12-31])"

        parameters = {
            "query": full_query,
            "resultType": "core",
            "synonym": "FALSE",
            "format": "xml",
            "fromSearchPost": "false",
        }

        content = []
        cursorMark = ""
        while len(content) < self.arguments.articles:
            try:
                parameters["cursorMark"] = cursorMark
                parameters["pageSize"] = min(
                    1000, self.arguments.articles - len(content)
                )

                url = urljoin(self.search_endpoint, f"?{urlencode(parameters)}")

                response = requests.get(url)
                response.raise_for_status()

                publication_documents, cursorMark = self.get_documents(
                    response=response.text
                )

                # No more articles
                if not publication_documents:
                    break

                content.extend(publication_documents)

                # No more pages to navigate
                if cursorMark is None:
                    break
            except requests.exceptions.RequestException:
                raise Exception("Error connecting to the Europe PMC API")

        return content

    def transform(self, source: sources.EuropePMC) -> documents.Collection:
        super().transform(source=source)

        content = self.extract()

        return documents.Collection.new_from(
            source, content=content, context=self.context(exclude=["query"])
        )
