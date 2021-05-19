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

from bs4 import BeautifulSoup
from typing_extensions import Literal

from .pubmed_source_create_text_collection_document import Transformer as TTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(TTransformer):
    """
    Extracts documents from PubMed API and returns a
    collection of Text documents for each article.

    Parameters
    ----------
    terms : list
        Keywords to look for
    articles: int
        The number of articles to retrieve
    hours: int
        Hours to look back from now
    """

    type: Literal[__script__] = __script__

    def get_params(self):
        return "abstract", "xml"

    def get_pmid(self, result):
        # needed for backwards compat
        soup = BeautifulSoup(result, "xml")
        pmid = soup.find("PMID").text

        return pmid

    def result_handler(self, raw_text):
        soup = BeautifulSoup(raw_text, "xml")
        articles = soup.findAll("PubmedArticle")

        return [str(a) for a in articles]
