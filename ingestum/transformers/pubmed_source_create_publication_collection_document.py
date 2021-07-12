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

__script__ = os.path.basename(__file__).replace(".py", "")


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

        formatted_authors = []
        for author in res_authors:
            author_ln = author.find("LastName")
            author_ini = author.find("Initials")

            formatted_author = ""
            formatted_author += author_ln.string if author_ln is not None else ""
            formatted_author += (
                f", {author_ini.string}" if author_ini is not None else ""
            )
            formatted_authors.append(formatted_author)

        formatted_abstract = ""
        for abstract_portion in res_abstract:
            text_strings = abstract_portion.stripped_strings
            formatted_abstract += " "
            for text_string in text_strings:
                formatted_abstract += f"{text_string}"
        formatted_abstract = formatted_abstract[1:]

        formatted_date = ""
        month_dict = {
            "Jan": "01",
            "Feb": "02",
            "Mar": "03",
            "Apr": "04",
            "May": "05",
            "Jun": "06",
            "Jul": "07",
            "Aug": "08",
            "Sep": "09",
            "Oct": "10",
            "Nov": "11",
            "Dec": "12",
        }
        year = res_pub_date.find("Year")
        month = res_pub_date.find("Month")
        day = res_pub_date.find("Day")
        formatted_date += year.string if year is not None else "-"
        if month is not None:
            formatted_date += f"-{month_dict[month.string]}"
            if day is not None:
                formatted_date += f"-{day.string}"

        formatted_entrez_date = ""
        entrez_year = res_EDAT.find("Year")
        entrez_month = res_EDAT.find("Month")
        entrez_day = res_EDAT.find("Day")
        formatted_entrez_date += entrez_year.string if entrez_year is not None else "-"
        if entrez_month is not None:
            formatted_entrez_date += (
                f"-0{entrez_month.string}"
                if len(entrez_month.string) == 1
                else f"-{entrez_month.string}"
            )
            if entrez_day is not None:
                formatted_entrez_date += (
                    f"-0{entrez_day.string}"
                    if len(entrez_day.string) == 1
                    else f"-{entrez_day.string}"
                )

        publication["title"] = res_title.string[:-1] if res_title is not None else ""
        publication["abstract"] = formatted_abstract
        publication["keywords"] = (
            [keyword.string for keyword in res_keywords]
            if res_keywords is not None
            else []
        )
        publication["authors"] = formatted_authors
        publication["language"] = (
            res_language.string if res_language is not None else ""
        )
        publication["publication_date"] = formatted_date
        publication["journal"] = (
            res_journal.find("Title").string if res_journal is not None else ""
        )
        publication["origin"] = origin
        publication["references"] = (
            [ref.string for ref in res_references] if res_references is not None else ""
        )
        publication["journal_ISSN"] = res_ISSN.string if res_ISSN is not None else ""
        publication["entrez_date"] = formatted_entrez_date

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
        )

    # redundantly added for auto documentation
    def transform(self, source: sources.PubMed) -> documents.Collection:
        return super().transform(source=source)
