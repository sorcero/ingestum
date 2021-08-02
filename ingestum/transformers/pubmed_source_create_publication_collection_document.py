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

from bs4 import BeautifulSoup
from typing_extensions import Literal

from .pubmed_source_create_xml_collection_document import Transformer as TTransformer
from .. import sources
from .. import documents
from ..utils import date_from_string, date_to_default_format, date_string_from_xml_node
from urllib.parse import urljoin

__script__ = os.path.basename(__file__).replace(".py", "")

PUBMED_ABSTRACT_BASE_URL = "http://www.ncbi.nlm.nih.gov/pubmed/"


class Transformer(TTransformer):
    """
    Extracts documents from `PubMed` API and returns a collection of `Publication`
    documents.

    :param terms: PubMed queries
    :type terms: list
    :param articles: The number of publications to retrieve
    :type articles: int
    :param hours: Hours to look back from now
    :type hours: int
    """

    type: Literal[__script__] = __script__

    def get_document(self, source, origin, content):
        res_soup = BeautifulSoup(str(content), "xml")
        publication = {}

        res_title = res_soup.find("ArticleTitle")
        res_abstract = res_soup.findAll("AbstractText")
        res_language = res_soup.find("Language")
        res_authors = res_soup.findAll("Author")
        res_keywords = res_soup.findAll("Keyword")
        res_pub_date = res_soup.find("PubDate")
        res_journal = res_soup.find("Journal")
        res_references = res_soup.findAll("Citation")
        res_ISSN = res_soup.find("ISSN")
        res_EDAT = res_soup.find("PubMedPubDate", PubStatus="pubmed")
        res_medline_journal_info = res_soup.find("MedlineJournalInfo")
        res_country = res_medline_journal_info.find("Country")
        res_document_type = res_soup.findAll("PublicationType")
        res_provider_id = res_soup.find("PMID")

        formatted_authors = []
        for author in res_authors:
            author_ln = author.find("LastName")
            author_ini = author.find("Initials")

            normalized_name = ""
            normalized_name += author_ln.text if author_ln is not None else ""
            normalized_name += f", {author_ini.text}" if author_ini is not None else ""

            affiliation = [
                affiliation.text for affiliation in author.findAll("Affiliation")
            ]

            author_model = {"name": normalized_name, "affiliation": affiliation}

            formatted_authors.append(author_model)

        formatted_abstract = ""
        for abstract_portion in res_abstract:
            text_strings = abstract_portion.text
            formatted_abstract += f" {text_strings}"
        formatted_abstract = formatted_abstract[1:]

        publication["title"] = res_title.text[:-1] if res_title is not None else ""
        publication["abstract"] = formatted_abstract
        publication["keywords"] = (
            [keyword.text for keyword in res_keywords]
            if res_keywords is not None
            else []
        )
        publication["authors"] = formatted_authors
        publication["language"] = res_language.text if res_language is not None else ""
        publication["publication_date"] = date_to_default_format(
            date_from_string(date_string_from_xml_node(res_pub_date))
            if res_pub_date is not None
            else ""
        )
        publication["journal"] = (
            res_journal.find("Title").text if res_journal is not None else ""
        )
        publication["origin"] = origin
        publication["references"] = (
            [ref.text for ref in res_references] if res_references is not None else ""
        )
        publication["journal_ISSN"] = res_ISSN.text if res_ISSN is not None else ""
        publication["entrez_date"] = date_to_default_format(
            date_from_string(date_string_from_xml_node(res_EDAT))
            if res_EDAT is not None
            else ""
        )
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
            PUBMED_ABSTRACT_BASE_URL, publication["provider_id"]
        )

        return documents.Publication.new_from(
            source,
            title=publication["title"],
            origin=publication["origin"],
            abstract=publication["abstract"],
            keywords=publication["keywords"],
            authors=publication["authors"],
            language=publication["language"],
            publication_date=publication["publication_date"],
            journal=publication["journal"],
            references=publication["references"],
            journal_ISSN=publication["journal_ISSN"],
            entrez_date=publication["entrez_date"],
            provider="pubmed",
            provider_id=publication["provider_id"],
            provider_url=publication["provider_url"],
            country=publication["country"],
            publication_type=publication["publication_type"],
        )

    # redundantly added for auto documentation
    def transform(self, source: sources.PubMed) -> documents.Collection:
        return super().transform(source=source)
