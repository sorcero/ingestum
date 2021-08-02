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
import pycountry

from bs4 import BeautifulSoup
from typing_extensions import Literal

from .proquest_source_create_xml_collection_document import Transformer as TTransformer
from .. import sources
from .. import documents
from ..utils import date_from_string, date_to_default_format, sanitize_string
from urllib.parse import urljoin

__script__ = os.path.basename(__file__).replace(".py", "")

PROQUEST_ABSTRACT_BASE_URL = "https://www.proquest.com/docview/"


class Transformer(TTransformer):
    """
    Extracts documents from `ProQuest` API and returns a collection of `Publication`
    documents.

    :param query: Keywords to look for
    :type query: str

    :param databases: Databases to target
    :type databases: list

    :param articles: Maximum number of results
    :type articles: int
    """

    type: Literal[__script__] = __script__

    def get_authors(self, res_author_list):
        authors = []

        for author in res_author_list:
            surname = ""
            if surname := author.find("LastName"):
                surname = sanitize_string(surname.text)

            given_names = ""
            if given_names_data := author.find("FirstName"):
                given_names = sanitize_string(given_names_data.text)

            if not surname and not given_names:
                continue

            affiliation = []
            if affiliation_list := author.findAll("ContribCompanyName"):
                affiliation.extend(
                    [
                        affiliation_info.text.strip()
                        for affiliation_info in affiliation_list
                    ]
                )

            authors.append(
                documents.publication.Author(
                    name=f"{surname}, {given_names}", affiliation=affiliation
                )
            )

        return authors

    def get_keywords(self, res_keywords):
        keywords = []

        for keyword in res_keywords:
            formatted_keyword = ""
            if heading := keyword.find("Heading"):
                formatted_keyword += heading.text.strip()
            if heading_qualifier := keyword.find("HeadingQualifier"):
                formatted_keyword += f", {heading_qualifier.text.strip()}"
            keywords.append(formatted_keyword)

        return keywords

    def get_document(self, source, origin, content):
        res_soup = BeautifulSoup(content, "xml")

        publication = {}

        res_title = res_soup.find("Title")
        res_abstract = res_soup.find("Abstract")
        res_author_list = res_soup.findAll("Contributor", ContribRole="Author")
        res_language = res_soup.find("Language")
        res_pub_date = res_soup.find("PublicationDate")
        res_keywords = res_soup.findAll("HeadingTerm")
        res_journal = res_soup.find("PublicationTitle")
        res_references = res_soup.findAll("Reference")
        res_ISSN = res_soup.find("LocatorID", IDType="ISSN")
        res_country = res_soup.find("PublisherCountryName")
        res_document_type = res_soup.findAll("DocumentType")
        res_provider_id = res_soup.find("ProquestID")

        publication["title"] = res_title.text[:-1] if res_title is not None else ""
        publication["abstract"] = res_abstract.text if res_abstract is not None else ""
        publication["keywords"] = self.get_keywords(res_keywords)
        publication["authors"] = self.get_authors(res_author_list)
        publication["language"] = (
            pycountry.languages.get(name=res_language.text).alpha_3
            if res_language is not None
            else ""
        )
        publication["publication_date"] = (
            date_to_default_format(date_from_string(res_pub_date.text))
            if res_pub_date is not None
            else ""
        )
        publication["journal"] = res_journal.text if res_journal is not None else ""
        publication["references"] = (
            [ref.text.split(" ", 1)[1] for ref in res_references]
            if res_references is not None
            else ""
        )
        publication["journal_ISSN"] = res_ISSN.text if res_ISSN is not None else ""
        # XXX can't find entrez date
        publication["entrez_date"] = ""
        publication["country"] = res_country.text.title() if res_country else ""
        publication["publication_type"] = (
            [doc.text for doc in res_document_type]
            if res_document_type is not None
            else []
        )
        publication["provider_id"] = (
            res_provider_id.text if res_provider_id is not None else ""
        )
        publication["provider_url"] = urljoin(
            PROQUEST_ABSTRACT_BASE_URL, publication["provider_id"]
        )

        return documents.Publication.new_from(
            source,
            title=publication["title"],
            origin=origin,
            abstract=publication["abstract"],
            keywords=publication["keywords"],
            authors=publication["authors"],
            language=publication["language"],
            publication_date=publication["publication_date"],
            journal=publication["journal"],
            references=publication["references"],
            journal_ISSN=publication["journal_ISSN"],
            entrez_date=publication["entrez_date"],
            provider="proquest",
            provider_id=publication["provider_id"],
            provider_url=publication["provider_url"],
            country=publication["country"],
            publication_type=publication["publication_type"],
        )

    # redundantly added for auto documentation
    def transform(self, source: sources.ProQuest) -> documents.Collection:
        return super().transform(source=source)
