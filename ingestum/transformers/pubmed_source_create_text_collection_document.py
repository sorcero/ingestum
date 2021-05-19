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
import datetime
import entrezpy
import entrezpy.conduit

from pydantic import BaseModel
from typing import Optional, List
from typing_extensions import Literal

from .base import BaseTransformer
from .. import sources
from .. import documents

__script__ = os.path.basename(__file__).replace(".py", "")

PUBMED_ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
PUBMED_EFETCH = "efetch.fcgi"
PUBMED_DB = "pubmed"


class PubMedResult(entrezpy.base.result.EutilsResult):
    def __init__(self, response, request):
        super().__init__(request.eutil, request.query_id, request.db)
        self._texts = []

    def add(self, raw_text, handler):
        for result in handler(raw_text):
            self._texts.append(result)

    def dump(self):
        return self._texts

    def size(self):
        return len(self._texts)


class PubMedAnalyzer(entrezpy.base.analyzer.EutilsAnalyzer):
    def __init__(self, handler):
        super().__init__()
        self._handler = handler

    def init_result(self, response, request):
        if self.result is None:
            self.result = PubMedResult(response, request)

    def analyze_result(self, response, request):
        self.init_result(response, request)
        self.result.add(response.read(), self._handler)

    def get_results(self):
        return self.result.dump()


class PubMedService:
    @classmethod
    def search_and_fetch(self, email, db, term, retmax, retmode, rettype, handler):
        conduit = entrezpy.conduit.Conduit(email)

        pipeline = conduit.new_pipeline()

        sid = pipeline.add_search(
            {
                "db": db,
                "term": term,
            }
        )

        pipeline.add_fetch(
            {
                "retmax": retmax,
                "retmode": retmode,
                "rettype": rettype,
            },
            dependency=sid,
            analyzer=PubMedAnalyzer(handler),
        )

        result = conduit.run(pipeline)
        return result.get_results()


class Transformer(BaseTransformer):
    """
    Extracts documents from PubMed API and returns a
    collection of TEXT documents for each article.

    Parameters
    ----------
    terms : list
        Keywords to look for
    articles: int
        The number of articles to retrieve
    hours: int
        Hours to look back from now
    """

    class ArgumentsModel(BaseModel):
        terms: List[str]
        articles: int
        hours: int

    class InputsModel(BaseModel):
        source: sources.PubMed

    class OutputsModel(BaseModel):
        document: documents.Collection

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def get_start(self, source):
        delta = datetime.timedelta(hours=self.arguments.hours)
        end = datetime.datetime.now()
        start = end - delta

        return start

    def get_term(self, source):
        terms = "OR".join(
            [f"({term.replace(' ', '+')})" for term in self.arguments.terms]
        )
        terms += f'(("{self.get_start(source).isoformat()}"[Date - Publication] : "3000"[Date - Publication]))'

        return terms

    def get_params(self):
        return "medline", "text"

    def get_pmid(self, result):
        pattern = re.compile(r"^PMID- (.*)$", re.MULTILINE)
        match = pattern.search(result)
        pmid = match.group(1)

        return pmid

    def result_handler(self, raw_text):
        return raw_text.split("\n\n")

    def extract(self, source):
        contents = []

        pubmed_type, pubmed_retmode = self.get_params()
        results = PubMedService.search_and_fetch(
            source.email,
            PUBMED_DB,
            self.get_term(source),
            self.arguments.articles,
            pubmed_retmode,
            pubmed_type,
            self.result_handler,
        )

        for result in results:
            # needed for backwards compat
            pmid = self.get_pmid(result)
            origin = f"{PUBMED_ENDPOINT}/{PUBMED_EFETCH}?db={PUBMED_DB}&id={pmid}&rettype={pubmed_type}&retmode={pubmed_retmode}"

            document = documents.Text.new_from(None, origin=origin, content=result)
            contents.append(document)

        return contents

    def transform(self, source):
        super().transform(source=source)

        content = self.extract(source)

        return documents.Collection.new_from(
            source,
            content=content,
            context=self.context(),
        )
