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
import datetime
import entrezpy
import entrezpy.conduit

from urllib.parse import urlencode, urljoin
from pydantic import BaseModel
from typing import Optional, List
from typing_extensions import Literal

from .base import BaseTransformer
from .. import sources
from .. import documents

__logger__ = logging.getLogger("ingestum")
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

    def analyze_error(self, response, request):
        raise Exception("Could not run PubMed pipeline: response error")

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

        if result.isEmpty():
            return []
        elif result.isSuccess() is False:
            raise Exception("Could not run PubMed pipeline: did not succeed")
        elif not hasattr(result, "get_results"):
            raise Exception("Could not run PubMed pipeline: unspecified error")

        return result.get_results()


class Transformer(BaseTransformer):
    """
    Extracts documents from `PubMed` API and returns a collection of `Text`
    documents for each article.

    :param terms: Keywords to look for
    :type terms: list
    :param articles: The number of articles to retrieve
    :type articles: int
    :param hours: Hours to look back from now
    :type hours: int
    :param from_date: Lower entrez date range limit
    :type from_date: str
    :param to_date: Upper entrez date range limit
    :type to_date: str
    """

    class ArgumentsModel(BaseModel):
        terms: List[str]
        articles: int
        hours: Optional[int] = -1
        from_date: Optional[str] = ""
        to_date: Optional[str] = ""

    class InputsModel(BaseModel):
        source: sources.PubMed

    class OutputsModel(BaseModel):
        document: documents.Collection

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def get_start(self):
        delta = datetime.timedelta(hours=self.arguments.hours)
        end = datetime.datetime.now()
        start = end - delta

        return start

    def get_term(self):
        term = "OR".join([t for t in self.arguments.terms])

        has_hours = self.arguments.hours > 0
        has_from = self.arguments.from_date != ""
        has_to = self.arguments.to_date != ""

        if has_hours and (has_from or has_to):
            logging.warning(
                "Arguments 'hours' and 'from_date/to_date' are mutually exclusive ('hours' will be ignored)"
            )

        if has_from and has_to:
            term += f" AND {self.arguments.from_date.replace('-', '/')}:{self.arguments.to_date.replace('-', '/')}[EDAT]"
        elif has_from:
            term += (
                f" AND {self.arguments.from_date.replace('-', '/')}:3000/12/31[EDAT]"
            )
        elif has_to:
            term += f" AND 1900/01/01:{self.arguments.to_date.replace('-', '/')}[EDAT]"
        elif has_hours:
            start = self.get_start()
            edat = "%d/%02d/%d" % (start.year, start.month, start.day)
            term += f' AND ("{edat}"[EDAT] : "3000/12/31"[EDAT])'

        return term

    def get_params(self):
        return "medline", "text"

    def get_pmid(self, result):
        pattern = re.compile(r"^PMID- (.*)$", re.MULTILINE)
        match = pattern.search(result)
        pmid = match.group(1)

        return pmid

    def is_valid(self, result):
        return "Error occurred:" not in result

    def result_handler(self, raw_text):
        return raw_text.split("\n\n")

    def get_document(self, source, origin, content):
        return documents.Text.new_from(source, origin=origin, content=content)

    def extract(self, source):
        contents = []

        pubmed_type, pubmed_retmode = self.get_params()

        try:
            results = PubMedService.search_and_fetch(
                source.email,
                PUBMED_DB,
                self.get_term(),
                self.arguments.articles,
                pubmed_retmode,
                pubmed_type,
                self.result_handler,
            )
        except Exception as e:
            __logger__.error(str(e), extra={"props": {"transformer": self.type}})
            results = []

        for result in results:
            if not self.is_valid(result):
                __logger__.error("missing", extra={"props": {"transformer": self.type}})
                continue

            # needed for backwards compat
            query = {
                "id": self.get_pmid(result),
                "db": PUBMED_DB,
                "rettype": pubmed_type,
                "retmode": pubmed_retmode,
            }
            origin = urljoin(
                f"{PUBMED_ENDPOINT}/{PUBMED_EFETCH}", f"?{urlencode(query)}"
            )

            document = self.get_document(source=source, origin=origin, content=result)
            contents.append(document)

        return contents

    def transform(self, source: sources.PubMed) -> documents.Collection:
        super().transform(source=source)

        content = self.extract(source)

        return documents.Collection.new_from(
            source,
            content=content,
            context=self.context(),
        )
