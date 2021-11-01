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
import time
import math
import logging
import requests
import datetime
import pycountry

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urljoin, quote

from .. import documents
from .. import sources
from .. import utils
from .base import BaseTransformer

__logger__ = logging.getLogger("ingestum")
__script__ = os.path.basename(__file__).replace(".py", "")

MAX_PER_PAGE = 75
MAX_ARTICLES = 2000
MIN_DELAY = 0.333

REPOS = {
    "biorxiv": {
        "search_url": os.environ.get(
            "INGESTUM_BIORXIV_SEARCH_URL", "https://www.biorxiv.org/search/"
        ),
        "content_url": os.environ.get(
            "INGESTUM_BIORXIV_CONTENT_URL", "https://www.biorxiv.org/content/"
        ),
    },
    "medrxiv": {
        "search_url": os.environ.get(
            "INGESTUM_MEDRXIV_SEARCH_URL", "https://www.medrxiv.org/search/"
        ),
        "content_url": os.environ.get(
            "INGESTUM_MEDRXIV_CONTENT_URL", "https://www.medrxiv.org/content/"
        ),
    },
}


class Transformer(BaseTransformer):
    """
    Transforms a `Biorxiv` source into a `Collection` of `Publication` documents

    :param query: biorxiv search query
    :type query: str
    :param articles: The number of publications to retrieve
    :type articles: int
    :param hours: Hours to look back from now
    :type hours: int
    :param from_date: Lower limit for posted date
    :type from_date: str
    :param to_date: Upper limit for posted date
    :type to_date: str
    :param repo: name of the publications repository (biorxiv or medrxiv)
    :type repo: str
    :param filters: extra filters for the biorxiv search URL
    :type filters: dict
    :param full_text: Extract the full text article if set to True (defaults to False)
    :type full_text: bool
    """

    class ArgumentsModel(BaseModel):
        query: str
        articles: int
        hours: Optional[int] = -1
        from_date: Optional[str] = ""
        to_date: Optional[str] = ""
        repo: str = "biorxiv"
        filters: Optional[dict] = {}
        full_text: Optional[bool] = False

    class InputsModel(BaseModel):
        source: sources.Biorxiv

    class OutputsModel(BaseModel):
        document: documents.Collection

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def get_authors(self, xml):
        authors = []

        for author in xml.findAll("contrib"):
            surname = ""
            if surname_data := author.find("surname"):
                surname = utils.sanitize_string(surname_data.text)

            given_names = ""
            if given_names_data := author.find("given-names"):
                given_names = utils.sanitize_string(given_names_data.text)

            if not surname and not given_names:
                continue

            affiliation = []
            ref_data = author.findAll("xref", attrs={"ref-type": "aff"})
            for ref in ref_data:
                if affiliation_data := xml.find("aff", attrs={"id": ref["rid"]}):
                    if affiliation_label := affiliation_data.find("label"):
                        affiliation_label.extract()
                    affiliation.append(affiliation_data.text.strip())

            authors.append(
                documents.publication.Author(
                    name=f"{surname}, {given_names}", affiliation=affiliation
                )
            )

        return authors

    def get_date(self, date_data):
        publication_date = ""

        # XXX we should re-evaluate these utils and merge these into one
        publication_date = utils.date_string_from_xml_node(
            date_data, "year", "month", "day"
        )
        publication_date = utils.date_from_string(publication_date)
        publication_date = utils.date_to_default_format(publication_date)

        return publication_date

    def get_keywords(self, keywords_data):
        keywords = []

        for keyword in keywords_data.findAll("kwd"):
            keywords.append(utils.sanitize_string(keyword.text))

        return keywords

    def get_references(self, references_data):
        references = []

        for reference in references_data.findAll("citation"):
            references.append(utils.sanitize_string(reference.text))

        return references

    def get_full_text(self, full_text_url):
        __logger__.debug(
            "extracting full text",
            extra={"props": {"transformer": self.type, "url": full_text_url}},
        )

        try:
            headers = {"User-Agent": "Ingestum", "Connection": "close"}
            response = requests.get(full_text_url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            __logger__.error(
                "missing",
                extra={
                    "props": {
                        "transformer": self.type,
                        "url": full_text_url,
                        "error": str(e),
                    }
                },
            )
            return ""

        soup = BeautifulSoup(response.content, "lxml")
        full_text_node = soup.find("div", {"class": "article fulltext-view"})

        if full_text_node is None:
            return ""
        return full_text_node.text

    def get_publication(self, repo, url):
        try:
            headers = {"User-Agent": "Ingestum", "Connection": "close"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            __logger__.error(
                "missing",
                extra={
                    "props": {"transformer": self.type, "url": url, "error": str(e)}
                },
            )
            return None

        # handle publication
        soup = BeautifulSoup(response.text, "lxml")

        # handle title
        title = ""
        if title_data := soup.find("article-title"):
            title = title_data.text

        # handle abstract
        abstract = ""
        if abstract_data := soup.find("abstract"):
            if abstract_title := abstract_data.find("title"):
                abstract_title.extract()
            abstract = abstract_data.text

        # handle authors
        authors = self.get_authors(soup)

        # handle publication date
        publication_date = self.get_date(
            soup.find("date", attrs={"date-type": "accepted"})
        )

        # handle journal
        journal_data = soup.find("journal-meta")

        journal = ""
        if journal_data and (journal_title := journal_data.find("journal-title")):
            journal = journal_title.text

        journal_ISSN = ""
        if journal_data and (journal_issn := journal_data.find("issn")):
            journal_ISSN = journal_issn.text

        # handle entrez date
        entrez_date = self.get_date(soup.find("date", attrs={"date-type": "accepted"}))

        # handle provider
        provider_data = soup.find("article-meta")

        provider = self.arguments.repo

        provider_id = ""
        if provider_data and (
            article_id := provider_data.find("article-id", attrs={"pub-id-type": "doi"})
        ):
            provider_id = article_id.text

        provider_url = ""
        if provider_id:
            provider_url = urljoin(repo["content_url"], provider_id)

        # handle full text
        full_text_url = ""
        if provider_url:
            full_text_url = f"{provider_url}.full"

        # handle language
        language = ""
        if language_data := soup.find("article"):
            if code := language_data.get("xml:lang"):
                language = pycountry.languages.get(alpha_2=code).alpha_3

        # handle keywords
        keywords = self.get_keywords(soup)

        # handle references
        references = self.get_references(soup)

        # handle conflict of interest statement
        coi_statement = ""
        if coi_node := soup.find(
            "notes", {"notes-type": "competing-interest-statement"}
        ):
            if coi_statement := coi_node.find("p"):
                coi_statement = coi_statement.text

        # handle DOI
        doi = ""
        if doi_node := soup.find("article-id", {"pub-id-type": "doi"}):
            doi = doi_node.text

        # handle copyright
        copyright = ""
        if copyright_node := soup.find("copyright-statement"):
            copyright = copyright_node.text

        # handle content
        if self.arguments.full_text:
            content = self.get_full_text(full_text_url)
        else:
            content = ""

        # create publication doc
        return documents.Publication.new_from(
            None,
            title=title,
            origin=url,
            abstract=abstract,
            authors=authors,
            publication_date=publication_date,
            journal=journal,
            journal_ISSN=journal_ISSN,
            entrez_date=entrez_date,
            provider=provider,
            provider_id=provider_id,
            provider_url=provider_url,
            full_text_url=full_text_url,
            keywords=keywords,
            language=language,
            references=references,
            coi_statement=coi_statement,
            doi=doi,
            copyright=copyright,
            content=content,
        )

    def get_page(self, articles, page=None):
        repo = REPOS.get(self.arguments.repo)

        filters = {
            "jcode": self.arguments.repo,
            "numresults": articles,
        }

        if page is not None:
            filters["page"] = page

        has_hours = self.arguments.hours > 0
        has_from = self.arguments.from_date != ""
        has_to = self.arguments.to_date != ""

        if has_hours and (has_from or has_to):
            logging.warning(
                "Arguments 'hours' and 'from_date/to_date' are mutually exclusive ('hours' will be ignored)"
            )

        if has_from and has_to:
            filters["limit_from"] = self.arguments.from_date
            filters["limit_to"] = self.arguments.to_date
        elif has_from:
            filters["limit_from"] = self.arguments.from_date
            filters["limit_to"] = "3000-12-31"
        elif has_to:
            filters["limit_from"] = "1900-01-01"
            filters["limit_to"] = self.arguments.to_date
        elif has_hours:
            delta = datetime.timedelta(hours=self.arguments.hours)
            limit_to = datetime.datetime.now()
            limit_from = limit_to - delta

            filters["limit_from"] = limit_from.strftime("%Y-%m-%d")
            filters["limit_to"] = "3000-12-31"

        if self.arguments.filters:
            filters.update(self.arguments.filters)

        # XXX better way to do this?
        filters = urlencode(filters)
        filters = filters.replace("&", " ")
        filters = filters.replace("=", ":")

        search = quote(f"{self.arguments.query} {filters}")
        url = urljoin(repo["search_url"], search)
        __logger__.debug(
            "searching", extra={"props": {"transformer": self.type, "url": url}}
        )

        try:
            headers = {"User-Agent": "Ingestum", "Connection": "close"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            __logger__.error(
                "missing",
                extra={
                    "props": {"transformer": self.type, "url": url, "error": str(e)}
                },
            )
            return None

        return response.text

    def process_page(self, body):
        content = []

        if not body:
            return content

        repo = REPOS.get(self.arguments.repo)

        soup = BeautifulSoup(body, "lxml")
        articles = soup.findAll("div", {"class": "highwire-article-citation"})
        for article in articles:
            # do not spam Biorxiv
            time.sleep(MIN_DELAY)

            # XXX only way to infer the XML resource path
            resource = article["data-apath"]
            resource = re.sub(r"^/\w+/", "", resource)
            resource = resource.replace("atom", "source.xml")

            publication_url = urljoin(repo["content_url"], resource)
            publication = self.get_publication(repo, publication_url)

            if publication is not None:
                content.append(publication)

        return content

    def extract(self):
        content = []

        if self.arguments.articles < MAX_ARTICLES:
            page = self.get_page(self.arguments.articles)
            content += self.process_page(page)
        else:
            page = self.get_page(MAX_PER_PAGE)
            content += self.process_page(page)

            pages = 1
            soup = BeautifulSoup(page, "lxml")
            if pages_data := soup.find("li", {"class": "pager-last"}):
                pages = int(pages_data.text)

            needed_pages = int(math.ceil(self.arguments.articles / MAX_PER_PAGE))
            if pages > needed_pages:
                pages = needed_pages

            for index in range(2, pages + 1):
                page = self.get_page(MAX_PER_PAGE, index)
                content += self.process_page(page)

        return content

    def transform(self, source: sources.Biorxiv) -> documents.Collection:
        super().transform(source=source)

        content = self.extract()

        return documents.Collection.new_from(
            source, content=content, context=self.context()
        )
