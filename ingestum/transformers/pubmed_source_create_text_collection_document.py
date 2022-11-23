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

from bs4 import BeautifulSoup
from urllib.parse import urlencode, urljoin
from pydantic import BaseModel
from typing import Optional, List
from typing_extensions import Literal
from requests.exceptions import RequestException, ChunkedEncodingError

from .base import BaseTransformer
from .. import sources
from .. import documents
from .. import errors
from .. import utils

__logger__ = logging.getLogger("ingestum")
__script__ = os.path.basename(__file__).replace(".py", "")


PUBMED_ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
PUBMED_EFETCH = "efetch.fcgi"
PUBMED_DB = "pubmed"

BACKOFF = 5
RETRIES = min(int(os.environ.get("INGESTUM_PUBMED_MAX_ATTEMPTS", 1)), 5)


class PubMedService:
    @classmethod
    @utils.retry(attempts=RETRIES, backoff=BACKOFF, errors=(ChunkedEncodingError,))
    def search_and_fetch_best_effort(
        cls, email, key, db, term, retmax, retmode, rettype, cursor
    ):
        # Set auth data
        authorization = {
            "tool": "ingestum",
            "email": email,
            "db": db,
        }

        # Optional but, if set, the api_key MUST be valid
        if key is not None:
            authorization["api_key"] = key

        # Set retry policies for intermittent backend issues
        request = utils.create_request(
            total=RETRIES,
            backoff_factor=BACKOFF,
            status_forcelist=[400, 502],
            allowed_methods=["GET", "POST"],
        )

        # Call ESearch using POST to deal with long queries
        query = {
            "term": term,
            "sort": "relevance",
            "usehistory": "y",
        }
        query.update(authorization)

        url = f"{PUBMED_ENDPOINT}/esearch.fcgi"
        response = request.post(url, data=query)
        response.raise_for_status()

        # Parse results
        soup = BeautifulSoup(response.content, "lxml")

        # Check warnings
        if warn_list := soup.find("warninglist"):
            for warning in set([w.name for w in warn_list.find_all(recursive=False)]):
                __logger__.warning(
                    "backend",
                    extra={
                        "props": {
                            "warning": warning,
                        }
                    },
                )

        # Check errors
        if error_list := soup.find("errorlist"):
            for error in set([e.name for e in error_list.find_all(recursive=False)]):
                __logger__.error(
                    "backend",
                    extra={
                        "props": {
                            "error": error,
                        }
                    },
                )

        # Extract stats
        count = int(soup.find("count").text)

        # Check if empty
        if not count:
            return 0, ""

        # Extract references to the results set stored on backend
        web_env = soup.find("webenv").text
        query_key = soup.find("querykey").text

        # Call EFetch as usual
        query = {
            "query_key": query_key,
            "WebEnv": web_env,
            "rettype": rettype,
            "retmode": retmode,
            "retstart": cursor,
            "retmax": retmax,
        }
        query.update(authorization)

        url = f"{PUBMED_ENDPOINT}/efetch.fcgi"
        response = request.get(url, params=query)
        response.raise_for_status()

        return count, response.text


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
        return result and "Error occurred:" not in result

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
            total_results, results = PubMedService.search_and_fetch_best_effort(
                source.email,
                source.api_key,
                PUBMED_DB,
                self.get_term(),
                self.arguments.articles,
                pubmed_retmode,
                pubmed_type,
                self.arguments.cursor,
            )
            results = self.result_handler(results)
        except RequestException as e:
            code = e.response.status_code if e.response is not None else ""
            response = e.response.content if e.response is not None else ""
            __logger__.error(
                "backend",
                extra={
                    "props": {
                        "transformer": self.type,
                        "error_type": str(type(e).__name__),
                        "error_response": str(response),
                        "error_code": str(code),
                    }
                },
            )
            raise errors.BackendUnavailableError()

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

            try:
                document = self.get_document(
                    source=source, origin=origin, content=result
                )
            except Exception as e:
                __logger__.error(
                    "malformed",
                    extra={
                        "props": {
                            "transformer": self.type,
                            "error": str(e),
                            "origin": origin,
                        }
                    },
                )
                continue

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
