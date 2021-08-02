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
import logging
import requests
import datetime

from string import punctuation
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
    """

    class ArgumentsModel(BaseModel):
        query: str
        articles: int
        hours: int
        repo: str = "biorxiv"

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
                surname = surname_data.text.strip(punctuation)

            given_names = ""
            if given_names_data := author.find("given-names"):
                given_names = given_names_data.text.strip(punctuation)

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

    def get_publication(self, repo, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
        except:
            __logger__.error(
                "missing", extra={"props": {"transformer": self.type, "url": url}}
            )
            return None

        # handle publication
        soup = BeautifulSoup(response.text, "lxml")

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
            soup.find("pub-date", attrs={"date-type": "pub"})
        )

        # handle journal
        journal_data = soup.find("journal-meta")

        journal = ""
        if journal_data and (journal_title := journal_data.find("journal-title")):
            journal = journal_title.text

        journal_ISSN = ""
        if journal_data and (journal_issn := journal_data.find("issn")):
            journal = journal_issn.text

        # handle entrez date
        entrez_date = self.get_date(
            soup.find("pub-date", attrs={"pub-type": "hwp-created"})
        )

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

        full_text_url = ""
        if provider_url:
            full_text_url = f"{provider_url}.full"

        # create publication doc
        return documents.Publication.new_from(
            None,
            title=soup.find("article-title").text,
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
        )

    def extract(self):
        content = []

        repo = REPOS.get(self.arguments.repo)

        filters = {
            "jcode": self.arguments.repo,
            "numresults": self.arguments.articles,
        }

        if self.arguments.hours > 0:
            delta = datetime.timedelta(hours=self.arguments.hours)
            limit_to = datetime.datetime.now()
            limit_from = limit_to - delta

            filters["limit_from"] = limit_from.strftime("%Y-%m-%d")
            filters["limit_to"] = limit_to.strftime("%Y-%m-%d")

        # XXX better way to do this?
        filters = urlencode(filters)
        filters = filters.replace("&", " ")
        filters = filters.replace("=", ":")

        search = quote(f"{self.arguments.query} {filters}")
        url = urljoin(repo["search_url"], search)
        response = requests.get(url)

        soup = BeautifulSoup(response.text, "lxml")
        articles = soup.findAll("div", {"class": "highwire-article-citation"})
        for article in articles:
            # do not spam Biorxiv
            time.sleep(0.333)

            # XXX only way to infer the XML resource path
            resource = article["data-apath"]
            resource = re.sub(r"^/\w+/", "", resource)
            resource = resource.replace("atom", "source.xml")

            publication_url = urljoin(repo["content_url"], resource)
            publication = self.get_publication(repo, publication_url)

            if publication is not None:
                content.append(publication)

        return content

    def transform(self, source: sources.Biorxiv) -> documents.Collection:
        super().transform(source=source)

        content = self.extract()

        return documents.Collection.new_from(
            source, content=content, context=self.context()
        )
