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
import requests
import logging

from bs4 import BeautifulSoup
from typing_extensions import Literal
from typing import Optional

from .pubmed_source_create_xml_collection_document import Transformer as TTransformer
from .. import sources
from .. import documents
from ..utils import (
    date_from_string,
    date_to_default_format,
    date_string_from_xml_node,
    sanitize_string,
)
from urllib.parse import urljoin

__logger__ = logging.getLogger("ingestum")
__script__ = os.path.basename(__file__).replace(".py", "")

PUBMED_ABSTRACT_BASE_URL = "http://www.ncbi.nlm.nih.gov/pubmed/"
FULL_TEXT_BASE_URL = "https://www.ncbi.nlm.nih.gov/pmc/articles/"
PMCOA_BASE_URL = (
    "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/"
)


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
    :param from_date: Lower entrez date range limit
    :type from_date: str
    :param to_date: Upper entrez date range limit
    :type to_date: str
    :param full_text: Extract the full text article if set to True (defaults to False)
    :type full_text: bool
    """

    class ArgumentsModel(TTransformer.ArgumentsModel):
        full_text: Optional[bool] = False

    arguments: ArgumentsModel

    type: Literal[__script__] = __script__

    def get_authors(self, res_authors):
        authors = []

        for author in res_authors:
            surname = ""
            if surname := author.find("LastName"):
                surname = sanitize_string(surname.text)

            given_names = ""
            if given_names_data := author.find("ForeName"):
                given_names = sanitize_string(given_names_data.text)

            if not surname and not given_names:
                continue

            affiliation = []
            if affiliation_list := author.find_all("Affiliation"):
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

    def get_abstract_portion(self, res_abstract):
        portions = []

        for abstract_portion in res_abstract.find_all("AbstractText"):
            if abstract_portion.has_attr("Label"):
                portions.append(f"{abstract_portion['Label']}:")
            portions.append(f"{abstract_portion.text.strip()}")

        return " ".join(portions).strip()

    def get_abstract(self, root_node):
        portions = []

        if res_abstract := root_node.find("Abstract"):
            if abstract_text := self.get_abstract_portion(res_abstract):
                portions.append(abstract_text)

        if res_other_abstract := root_node.find("OtherAbstract"):
            # Using language ISO 639-2 codes
            if res_other_abstract.get("Language") == "eng":
                if other_abstract_text := self.get_abstract_portion(res_other_abstract):
                    portions.append(other_abstract_text)

        return " ".join(portions).strip()

    def get_date_string(self, date_node):
        date_string = date_string_from_xml_node(date_node)
        if date_string != "":
            return date_string

        if medline_date := date_node.find("MedlineDate"):
            if year := re.search("^(\d{4})", medline_date.text):
                date_string += year.group(1)
                if month := re.search("[\s-]([A-Za-z]{3})[\s-]", medline_date.text):
                    date_string += f"-{month.group(1)}"
        return date_string

    def standarize_date_string(self, string):
        return date_to_default_format(date_from_string(string))

    def get_publication_date(self, res_soup):
        article_node = res_soup.find("Article")
        if not article_node:
            return ""

        targets = ["Electronic", "Electronic-Print", "Electronic-eCollection"]
        if article_node.has_attr("PubModel") and article_node["PubModel"] in targets:
            if article_date_node := res_soup.find("ArticleDate", DateType="Electronic"):
                return self.standarize_date_string(
                    self.get_date_string(article_date_node)
                )

        # If previous conditions were not met we fallback to PubDate
        if pub_date_node := article_node.find("PubDate"):
            return self.standarize_date_string(self.get_date_string(pub_date_node))

        # if nothing else...
        return ""

    def get_full_text(self, pmcid, pmid):
        full_text = ""
        if pmcid is not None:
            full_text_url = f"{PMCOA_BASE_URL}{pmid}/unicode"
            __logger__.debug(
                "extracting full text",
                extra={"props": {"transformer": self.type, "url": full_text_url}},
            )

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

                content_nodes = soup.find_all("infon", {"key": "type"})
                for content_node in content_nodes:
                    parent_node = content_node.parent
                    section_node = parent_node.find("infon", {"key": "section_type"})
                    if content_node.text.lower() != "ref" and (
                        section_node is None or section_node.text.lower() != "ref"
                    ):
                        if text_node := parent_node.find("text"):
                            full_text += f" {sanitize_string((text_node.text))}\n"
                full_text = full_text[1:]

        if full_text == "":
            __logger__.error(
                "no full text available",
                extra={
                    "props": {
                        "transformer": self.type,
                        "provider_id": pmid,
                    }
                },
            )

        return full_text

    def get_document(self, source, origin, content):
        res_soup = BeautifulSoup(str(content), "xml")
        publication = {}

        res_title = res_soup.find("ArticleTitle")
        res_language = res_soup.find("Language")
        res_authors = res_soup.find_all("Author")
        res_keywords = res_soup.find_all("Keyword")
        res_journal = res_soup.find("Journal")
        res_journal_abbreviation = res_soup.find("ISOAbbreviation")
        res_references = res_soup.find_all("Citation")
        res_ISSN = res_soup.find("ISSN")
        res_volume = res_soup.find("Volume")
        res_issue = res_soup.find("Issue")
        res_EDAT = res_soup.find("PubMedPubDate", PubStatus="pubmed")
        res_medline_journal_info = res_soup.find("MedlineJournalInfo")
        res_country = res_medline_journal_info.find("Country")
        res_document_type = res_soup.find_all("PublicationType")
        res_provider_id = res_soup.find("PMID")
        res_PMCID = res_soup.find("ArticleId", IdType="pmc")
        res_COI_statement = res_soup.find("CoiStatement")
        res_DOI = res_soup.find("ELocationID", {"EIdType": "doi", "ValidYN": "Y"})
        res_DOI_alt = res_soup.find("ArticleId", {"IdType": "doi"})
        res_copyright = res_soup.find("CopyrightInformation")
        res_pagination = res_soup.find("MedlinePgn")

        publication["title"] = res_title.text[:-1] if res_title is not None else ""
        publication["abstract"] = self.get_abstract(res_soup)
        publication["keywords"] = (
            [keyword.text for keyword in res_keywords]
            if res_keywords is not None
            else []
        )
        publication["authors"] = self.get_authors(res_authors)
        publication["language"] = res_language.text if res_language is not None else ""
        publication["publication_date"] = self.get_publication_date(res_soup)
        publication["journal"] = (
            res_journal.find("Title").text if res_journal is not None else ""
        )
        publication["journal_abbreviation"] = (
            res_journal_abbreviation.text
            if res_journal_abbreviation is not None
            else ""
        )
        publication["origin"] = origin
        publication["references"] = (
            [ref.text for ref in res_references] if res_references is not None else ""
        )
        publication["journal_ISSN"] = res_ISSN.text if res_ISSN is not None else ""
        publication["journal_volume"] = (
            res_volume.text if res_volume is not None else ""
        )
        publication["journal_issue"] = res_issue.text if res_issue is not None else ""
        publication["entrez_date"] = date_to_default_format(
            date_from_string(self.get_date_string(res_EDAT))
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
        publication["full_text_url"] = (
            urljoin(FULL_TEXT_BASE_URL, res_PMCID.text) if res_PMCID is not None else ""
        )

        if self.arguments.full_text:
            publication["content"] = self.get_full_text(res_PMCID, res_provider_id.text)

        publication["coi_statement"] = (
            res_COI_statement.text if res_COI_statement is not None else ""
        )
        publication["copyright"] = (
            res_copyright.text if res_copyright is not None else ""
        )
        publication["pagination"] = (
            res_pagination.text if res_pagination is not None else ""
        )

        publication["doi"] = ""
        if res_DOI is not None:
            publication["doi"] = res_DOI.text
        elif res_DOI_alt is not None:
            publication["doi"] = res_DOI_alt.text

        publication["provider"] = "pubmed"

        return documents.Publication.new_from(source, **publication)

    # redundantly added for auto documentation
    def transform(self, source: sources.PubMed) -> documents.Collection:
        return super().transform(source=source)
