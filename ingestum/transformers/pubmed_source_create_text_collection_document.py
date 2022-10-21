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
from .. import errors

__logger__ = logging.getLogger("ingestum")
__script__ = os.path.basename(__file__).replace(".py", "")

PUBMED_ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
PUBMED_EFETCH = "efetch.fcgi"
PUBMED_DB = "pubmed"


class EsearhAnalyzer(entrezpy.esearch.esearch_analyzer.EsearchAnalyzer):
    pass


class EfetchAnalyzer(entrezpy.efetch.efetch_analyzer.EfetchAnalyzer):
    def init_result(self, response, request):
        self._raw_result = self.norm_response(response, request.rettype)
        self.result = True

    def analyze_result(self, response, request):
        self.init_result(response, request)

    def analyze_error(self, response, request):
        raise Exception("Could not run PubMed pipeline: response error")

    def get_raw_result(self):
        return self._raw_result


class PubMedService:
    @classmethod
    def search_and_fetch(self, email, db, term, retmax, retmode, rettype, cursor):
        conduit = entrezpy.conduit.Conduit(email)

        pipeline = conduit.new_pipeline()

        esearch_analyzer = EsearhAnalyzer()
        sid = pipeline.add_search(
            {
                "db": db,
                "term": term,
                "retstart": cursor,
                "retmax": retmax,
                "rettype": "uilist",
                "usehistory": False,
            },
            analyzer=esearch_analyzer,
        )

        efetch_analyzer = EfetchAnalyzer()
        pipeline.add_fetch(
            {
                "retmode": retmode,
                "rettype": rettype,
            },
            dependency=sid,
            analyzer=efetch_analyzer,
        )

        result = conduit.run(pipeline)

        if result.isEmpty():
            return 0, []
        elif result.isSuccess() is False:
            raise Exception("Could not run PubMed pipeline: did not succeed")
        elif not hasattr(result, "get_raw_result"):
            raise Exception("Could not run PubMed pipeline: unspecified error")

        return esearch_analyzer.query_size(), result.get_raw_result()


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
        terms: Optional[List[str]] = []
        articles: int
        hours: Optional[int] = -1
        from_date: Optional[str] = ""
        to_date: Optional[str] = ""
        cursor: Optional[int] = 0

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

        has_terms = self.arguments.terms != []
        has_hours = self.arguments.hours > 0
        has_from = self.arguments.from_date != ""
        has_to = self.arguments.to_date != ""

        if has_hours and (has_from or has_to):
            logging.warning(
                "Arguments 'hours' and 'from_date/to_date' are mutually exclusive ('hours' will be ignored)"
            )

        date_query = ""
        if has_from and has_to:
            date_query = f"{self.arguments.from_date.replace('-', '/')}:{self.arguments.to_date.replace('-', '/')}[EDAT]"
        elif has_from:
            date_query = (
                f"{self.arguments.from_date.replace('-', '/')}:3000/12/31[EDAT]"
            )
        elif has_to:
            date_query = f"1900/01/01:{self.arguments.to_date.replace('-', '/')}[EDAT]"
        elif has_hours:
            start = self.get_start()
            edat = "%d/%02d/%d" % (start.year, start.month, start.day)
            date_query = f'("{edat}"[EDAT] : "3000/12/31"[EDAT])'

        if has_terms:
            terms = "OR".join([t for t in self.arguments.terms])

        if has_terms and date_query != "":
            term = f"{terms} AND {date_query}"
        elif has_terms and date_query == "":
            term = terms
        elif not has_terms:
            term = date_query

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

        has_terms = self.arguments.terms != []
        has_hours = self.arguments.hours > 0
        has_from = self.arguments.from_date != ""
        has_to = self.arguments.to_date != ""

        if not has_terms and not has_from and not has_to and not has_hours:
            raise Exception(
                "Either 'terms', 'hours' or 'from_date/to_date' or some/all of them must be set"
            )

        contents = []

        pubmed_type, pubmed_retmode = self.get_params()

        try:
            total_results, results = PubMedService.search_and_fetch(
                source.email,
                PUBMED_DB,
                self.get_term(),
                self.arguments.articles,
                pubmed_retmode,
                pubmed_type,
                self.arguments.cursor,
            )
            results = self.result_handler(results)
        except SystemExit as e:
            __logger__.error(
                "backend",
                extra={
                    "props": {
                        "transformer": self.type,
                        "error": f"exited with code {str(e)}",
                    }
                },
            )
            raise errors.BackendUnavailableError()
        except Exception as e:
            __logger__.error(
                "backend", extra={"props": {"transformer": self.type, "error": str(e)}}
            )
            total_results = 0
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

        context = {
            "total_results": total_results,
            "previous_cursor": self.arguments.cursor,
            "next_cursor": self.arguments.cursor + self.arguments.articles,
        }

        return context, contents

    def transform(self, source: sources.PubMed) -> documents.Collection:
        super().transform(source=source)

        context, content = self.extract(source)
        context = {f"{self.type}_pagination": context}
        context.update(self.context(exclude=["terms"]))

        return documents.Collection.new_from(
            source,
            content=content,
            context=context,
        )
