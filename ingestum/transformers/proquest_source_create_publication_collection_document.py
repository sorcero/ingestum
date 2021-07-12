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

__script__ = os.path.basename(__file__).replace(".py", "")


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

        formatted_keywords = []
        for keyword in res_keywords:
            heading = keyword.find("Heading")
            heading_qualifier = keyword.find("HeadingQualifier")

            formatted_keyword = ""
            formatted_keyword += heading.string if heading is not None else ""
            formatted_keyword += (
                f", {heading_qualifier.string}" if heading_qualifier is not None else ""
            )
            formatted_keywords.append(formatted_keyword)

        publication["title"] = res_title.string[:-1] if res_title is not None else ""
        publication["abstract"] = (
            res_abstract.string if res_abstract is not None else ""
        )
        publication["keywords"] = formatted_keywords
        publication["authors"] = (
            [author.find("NormalizedName").string for author in res_author_list]
            if res_author_list is not None
            else []
        )
        publication["language"] = (
            pycountry.languages.get(name=res_language.string).alpha_3
            if res_language is not None
            else ""
        )
        publication["publication_date"] = (
            res_pub_date.string if res_pub_date is not None else ""
        )
        publication["journal"] = res_journal.string if res_journal is not None else ""
        publication["references"] = (
            [ref.string.split(" ", 1)[1] for ref in res_references]
            if res_references is not None
            else ""
        )
        publication["journal_ISSN"] = res_ISSN.string if res_ISSN is not None else ""
        # XXX can't find entrez date
        publication["entrez_date"] = ""

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
        )

    # redundantly added for auto documentation
    def transform(self, source: sources.ProQuest) -> documents.Collection:
        return super().transform(source=source)
