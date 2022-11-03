# -*- coding: utf-8 -*-

#
# Copyright (c) 2021,2022 Sorcero, Inc.
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
import time
import math
import logging
import datetime
import pycountry

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urljoin, quote

from .. import documents
from .. import sources
from .. import errors
from .. import utils
from .base import BaseTransformer

__logger__ = logging.getLogger("ingestum")
__script__ = os.path.basename(__file__).replace(".py", "")

MAX_PER_PAGE = 75
MIN_DELAY = 0.333
BACKOFF = 5
RETRIES = min(int(os.environ.get("INGESTUM_BIORXIV_MAX_ATTEMPTS", 1)), 5)


REPOS = {
    "biorxiv": {
        "search_url": os.environ.get(
            "INGESTUM_BIORXIV_SEARCH_URL", "https://www.biorxiv.org/search/"
        ),
        "content_url": os.environ.get(
            "INGESTUM_BIORXIV_CONTENT_URL", "https://www.biorxiv.org/content/"
        ),
    },
    "medrxiv": {
        "search_url": os.environ.get(
            "INGESTUM_MEDRXIV_SEARCH_URL", "https://www.medrxiv.org/search/"
        ),
        "content_url": os.environ.get(
            "INGESTUM_MEDRXIV_CONTENT_URL", "https://www.medrxiv.org/content/"
        ),
    },
}


class Transformer(BaseTransformer):
    """
    Transforms a `Biorxiv` source into a `Collection` of `Publication` documents

    :param query: biorxiv search query
    :type query: str
    :param articles: The number of publications to retrieve
    :type articles: int
    :param hours: Hours to look back from now
    :type hours: int
    :param from_date: Lower limit for posted date
    :type from_date: str
    :param to_date: Upper limit for posted date
    :type to_date: str
    :param repo: name of the publications repository (biorxiv or medrxiv)
    :type repo: str
    :param filters: extra filters for the biorxiv search URL
    :type filters: dict
    :param full_text: Extract the full text article if set to True (defaults to False)
    :type full_text: bool
    :param abstract_title_query: Biorxiv search query limited to abstract and title
    :type abstract_title_query: str
    :param abstract_title_flags: Matching either match-any or match-all
    :type abstract_title_flags: str
    :param sort: Sorting order either publication-date or relevance-rank
    :type sort: str
    :param direction: For publication-date either ascending or descending
    :type direction: str
    """

    class ArgumentsModel(BaseModel):
        query: Optional[str] = ""
        articles: int
        hours: Optional[int] = -1
        from_date: Optional[str] = ""
        to_date: Optional[str] = ""
        repo: str = "biorxiv"
        filters: Optional[dict] = {}
        full_text: Optional[bool] = False
        abstract_title_query: Optional[str] = ""
        abstract_title_flags: Optional[str] = ""
        sort: Optional[str] = ""
        direction: Optional[str] = ""
        cursor: Optional[int] = 0

    class InputsModel(BaseModel):
        source: sources.Biorxiv

    class OutputsModel(BaseModel):
        document: documents.Collection

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def get_authors(self, xml):
        authors = []

        for author in xml.find_all("contrib"):
            surname = ""
            if surname_data := author.find("surname"):
                surname = utils.sanitize_string(surname_data.text)

            given_names = ""
            if given_names_data := author.find("given-names"):
                given_names = utils.sanitize_string(given_names_data.text)

            if not surname and not given_names:
                continue

            affiliation = []
            ref_data = author.find_all("xref", attrs={"ref-type": "aff"})
            for ref in ref_data:
                if affiliation_data := xml.find("aff", attrs={"id": ref["rid"]}):
                    if affiliation_label := affiliation_data.find("label"):
                        affiliation_label.extract()
                    affiliation.append(affiliation_data.text.strip())

            authors.append(
                documents.publication.Author(
                    name=f"{surname}, {given_names}", affiliation=affiliation
                )
            )

        return authors

    def get_date(self, date_data):
        publication_date = ""

        # XXX we should re-evaluate these utils and merge these into one
        publication_date = utils.date_string_from_xml_node(
            date_data, "year", "month", "day"
        )
        publication_date = utils.date_from_string(publication_date)
        publication_date = utils.date_to_default_format(publication_date)

        return publication_date

    def get_keywords(self, keywords_data):
        keywords = []

        for keyword in keywords_data.find_all("kwd"):
            keywords.append(utils.sanitize_string(keyword.text))

        return keywords

    def get_references(self, references_data):
        references = []

        for reference in references_data.find_all("citation"):
            references.append(utils.sanitize_string(reference.text))

        return references

    def get_full_text(self, provider_id, full_text_url):
        __logger__.debug(
            "downloading",
            extra={"props": {"transformer": self.type, "url": full_text_url}},
        )

        full_text = ""
        try:
            headers = {"User-Agent": "Ingestum", "Connection": "close"}
            session = utils.create_request(total=RETRIES, backoff_factor=BACKOFF)
            response = session.get(full_text_url, headers=headers)
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
            if full_text_node := soup.find("div", {"class": "article fulltext-view"}):
                full_text = full_text_node.text

        if full_text == "":
            __logger__.error(
                "no full text available",
                extra={"props": {"transformer": self.type, "provider_id": provider_id}},
            )
        return full_text

    def get_abstract(self, abstract_data):
        # remove redundant "Abstract" title
        if abstract_title := abstract_data.find("title"):
            abstract_title.extract()

        # format subtitles from "Conclusion" to " CONCLUSION "
        if section_titles := abstract_data.find_all("title"):
            for index, section_title in enumerate(section_titles):
                if not section_title.text:
                    continue

                title = section_title.text.strip()
                if not title:
                    continue

                prefix = " " if index > 0 else ""
                suffix = " " if title.endswith(":") else ": "
                section_title.string = f"{prefix}{title.upper()}{suffix}"

        return abstract_data.text

    def get_repo(self, journal_data):
        if hasattr(self.arguments, "repo"):
            return self.arguments.repo
        elif journal_data and (
            journal_title_node := journal_data.find("journal-title")
        ):
            return journal_title_node.text.strip().lower()
        return None

    def get_publication(self, xml, url):
        # handle publication
        soup = BeautifulSoup(xml, "lxml")

        # handle title
        title = ""
        if title_data := soup.find("article-title"):
            title = title_data.text

        # handle abstract
        abstract = ""
        if abstract_data := soup.find("abstract"):
            abstract = self.get_abstract(abstract_data)

        # handle authors
        authors = self.get_authors(soup)

        # handle publication date
        publication_date = ""
        if accepted_date_data := soup.find("date", attrs={"date-type": "accepted"}):
            publication_date = self.get_date(accepted_date_data)
        elif received_date_data := soup.find("date", attrs={"date-type": "received"}):
            publication_date = self.get_date(received_date_data)

        # handle journal
        journal_data = soup.find("journal-meta")

        journal = ""
        if journal_data and (journal_title := journal_data.find("journal-title")):
            journal = journal_title.text

        journal_abbreviation = ""
        if journal_data and (
            journal_abbreviation_data := journal_data.find("abbrev-journal-title")
        ):
            journal_abbreviation = journal_abbreviation_data.text

        journal_ISSN = ""
        if journal_data and (journal_issn := journal_data.find("issn")):
            journal_ISSN = journal_issn.text

        # handle entrez date
        entrez_date = publication_date

        # handle provider
        provider_data = soup.find("article-meta")

        provider = self.get_repo(journal_data)

        provider_id = ""
        if provider_data and (
            article_id := provider_data.find("article-id", attrs={"pub-id-type": "doi"})
        ):
            provider_id = article_id.text

        repo = REPOS.get(self.get_repo(journal_data))
        provider_url = ""
        if provider_id:
            provider_url = urljoin(repo["content_url"], provider_id)

        # handle full text
        full_text_url = ""
        if provider_url:
            full_text_url = f"{provider_url}.full"

        # handle language
        language = ""
        if language_data := soup.find("article"):
            if code := language_data.get("xml:lang"):
                language = pycountry.languages.get(alpha_2=code).alpha_3

        # handle keywords
        keywords = self.get_keywords(soup)

        # handle references
        references = self.get_references(soup)

        # handle conflict of interest statement
        coi_statement = ""
        if coi_node := soup.find(
            "notes", {"notes-type": "competing-interest-statement"}
        ):
            if coi_statement := coi_node.find("p"):
                coi_statement = coi_statement.text

        # handle DOI
        doi = ""
        if doi_node := soup.find("article-id", {"pub-id-type": "doi"}):
            doi = doi_node.text

        # handle copyright
        copyright = ""
        if copyright_node := soup.find("copyright-statement"):
            copyright = copyright_node.text

        # handle content
        if self.arguments.full_text:
            content = self.get_full_text(provider_id, full_text_url)
        else:
            content = ""

        # handle publication_type
        publication_type = ["Preprint"]

        # create publication doc
        return documents.Publication.new_from(
            None,
            title=title,
            origin=url,
            abstract=abstract,
            authors=authors,
            publication_date=publication_date,
            publication_type=publication_type,
            journal=journal,
            journal_abbreviation=journal_abbreviation,
            journal_ISSN=journal_ISSN,
            entrez_date=entrez_date,
            provider=provider,
            provider_id=provider_id,
            provider_url=provider_url,
            full_text_url=full_text_url,
            keywords=keywords,
            language=language,
            references=references,
            coi_statement=coi_statement,
            doi=doi,
            copyright=copyright,
            content=content,
        )

    def get_page(self, page):
        repo = REPOS.get(self.arguments.repo)

        if self.arguments.query and self.arguments.abstract_title_query:
            raise ValueError("query and abstract_title_query are mutually exclusive")

        filters = {
            "jcode": self.arguments.repo,
            "numresults": MAX_PER_PAGE,
        }

        has_hours = self.arguments.hours > 0
        has_from = self.arguments.from_date != ""
        has_to = self.arguments.to_date != ""

        if has_hours and (has_from or has_to):
            logging.warning(
                "Arguments 'hours' and 'from_date/to_date' are mutually exclusive ('hours' will be ignored)"
            )

        if has_from and has_to:
            filters["limit_from"] = self.arguments.from_date
            filters["limit_to"] = self.arguments.to_date
        elif has_from:
            filters["limit_from"] = self.arguments.from_date
            filters["limit_to"] = "3000-12-31"
        elif has_to:
            filters["limit_from"] = "1900-01-01"
            filters["limit_to"] = self.arguments.to_date
        elif has_hours:
            delta = datetime.timedelta(hours=self.arguments.hours)
            limit_to = datetime.datetime.now()
            limit_from = limit_to - delta

            filters["limit_from"] = limit_from.strftime("%Y-%m-%d")
            filters["limit_to"] = "3000-12-31"

        if self.arguments.abstract_title_query:
            filters["abstract_title"] = self.arguments.abstract_title_query
        if self.arguments.abstract_title_flags:
            filters["abstract_title_flags"] = self.arguments.abstract_title_flags
        if self.arguments.sort:
            filters["sort"] = self.arguments.sort
        if self.arguments.direction:
            filters["direction"] = self.arguments.direction

        if self.arguments.filters:
            filters.update(self.arguments.filters)

        # XXX better way to do this?
        filters = urlencode(filters)
        filters = filters.replace("&", " ")
        filters = filters.replace("=", ":")

        # XXX backend treats this as a special case
        page_filter = ""
        if page:
            page_filter = f"?page={page}"

        if self.arguments.query:
            search = quote(f"{self.arguments.query} {filters}")
        else:
            search = quote(f"{filters}")

        url = urljoin(repo["search_url"], f"{search}{page_filter}")

        try:
            headers = {"User-Agent": "Ingestum", "Connection": "close"}
            session = utils.create_request(total=RETRIES, backoff_factor=BACKOFF)
            response = session.get(url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            __logger__.error(
                "missing",
                extra={
                    "props": {
                        "transformer": self.type,
                        "error_type": str(type(e).__name__),
                    }
                },
            )
            raise errors.BackendUnavailableError()

        return response.text

    def download_url(self, url):
        __logger__.debug(
            "downloading",
            extra={"props": {"transformer": self.type, "url": url}},
        )

        try:
            headers = {"User-Agent": "Ingestum", "Connection": "close"}
            session = utils.create_request(total=RETRIES, backoff_factor=BACKOFF)
            response = session.get(url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            __logger__.error(
                "missing",
                extra={
                    "props": {"transformer": self.type, "url": url, "error": str(e)}
                },
            )
            return None
        else:
            return response.text

    def process_page(self, body, start_article, end_article):
        content = []

        if not body:
            return content

        repo = REPOS.get(self.arguments.repo)

        soup = BeautifulSoup(body, "lxml")
        articles = soup.find_all("div", {"class": "highwire-article-citation"})
        for article in articles[start_article:end_article]:
            # do not spam Biorxiv
            time.sleep(MIN_DELAY)

            # XXX only way to infer the XML resource path
            resource = article["data-apath"]
            resource = re.sub(r"^/\w+/", "", resource)
            resource = resource.replace("atom", "source.xml")

            publication_url = urljoin(repo["content_url"], resource)

            try:
                publication = self.get_publication(
                    self.download_url(publication_url), publication_url
                )
            except Exception as e:
                __logger__.error(
                    "malformed",
                    extra={
                        "props": {
                            "transformer": self.type,
                            "url": publication_url,
                            "error": str(e),
                        }
                    },
                )
                continue

            if publication is not None:
                content.append(publication)

        return content

    def get_pagination_info(self, content):
        articles_now = len(content)
        articles_total = self.arguments.cursor + articles_now
        articles_remaining = self.arguments.articles - articles_now

        page = int(articles_total / MAX_PER_PAGE)
        start = articles_total % MAX_PER_PAGE
        end = min(start + articles_remaining, MAX_PER_PAGE)

        return page, start, end

    def get_needed_pages(self, page, content):
        pages = 1

        pages_soup = BeautifulSoup(page, "lxml")
        pages_selectors = ["li.pager-item.last", "li.pager-last.last"]
        for selector in pages_selectors:
            if pages_data := pages_soup.select(selector):
                pages = int(pages_data[0].text)
                break

        needed_articles = self.arguments.cursor + self.arguments.articles
        needed_pages = int(math.ceil(needed_articles / MAX_PER_PAGE))

        if pages > needed_pages:
            pages = needed_pages

        return pages

    def get_total_articles(self, page):
        total = 0

        soup = BeautifulSoup(page, "lxml")
        if node := soup.find("h1", {"id": "page-title"}):
            if groups := re.findall(r"(^[\d|,]+)", node.text.strip()):
                total = int(groups[0].replace(",", ""))

        return total

    def extract(self):
        content = []

        current_page, start_article, end_article = self.get_pagination_info(content)
        page = self.get_page(current_page)
        content += self.process_page(page, start_article, end_article)

        total_articles = self.get_total_articles(page)
        if total_articles and self.arguments.cursor >= total_articles:
            raise ValueError(
                f"Cursor {self.arguments.cursor} can't be larger than or equal to the total {total_articles}"
            )

        pages = self.get_needed_pages(page, content)
        for page_index in range(current_page + 1, pages):
            time.sleep(MIN_DELAY)
            _, start_article, end_article = self.get_pagination_info(content)
            page = self.get_page(page_index)
            content += self.process_page(page, start_article, end_article)

        context = {
            "total_results": total_articles,
            "previous_cursor": self.arguments.cursor,
            "next_cursor": self.arguments.cursor + len(content),
        }

        return content, context

    def transform(self, source: sources.Biorxiv) -> documents.Collection:
        super().transform(source=source)

        content, _context = self.extract()

        context = self.context(exclude=["query", "abstract_title_query"])
        context[f"{self.type}_pagination"] = _context

        return documents.Collection.new_from(
            source,
            content=content,
            context=context,
        )
