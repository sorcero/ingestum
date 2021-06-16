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
import logging

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from .. import sources
from .base import BaseTransformer

__logger__ = logging.getLogger("ingestum")
__script__ = os.path.basename(__file__).replace(".py", "")

# "Clients connecting via OAuth2 may make up to 60 requests per minute."
# https://github.com/reddit-archive/reddit/wiki/API#rules
# QUERY_CALLS_LIMIT = 60
QUERY_CALLS_LIMIT = 1


class Transformer(BaseTransformer):
    """
    Transforms a Reddit source into a Collection of Form
    documents with the submissions of a subreddit.

    Parameters
    ----------
    search : str
        The search string to pass to a Reddit query, e.g., "python"
        https://www.reddit.com/search/?q=python
    subreddit : str
        Limit search results to the subreddit if provided
    sort : str
        The sorting criteria for the search
        The options are: "relevance", "hot", "new", "top", "comments"
        (Default: "relevance")
    """

    class ArgumentsModel(BaseModel):
        search: str
        subreddit: Optional[str]
        sort: Optional[str]

    class InputsModel(BaseModel):
        source: sources.Reddit

    class OutputsModel(BaseModel):
        document: documents.Collection

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def search_reddit(self, source, search_query, subreddit_name):
        submissions = []

        # Get Twython instantiate.
        python_reddit = source.get_reddit()

        # Generate queries.
        q_count = 100  # max allowed per query
        # Pull the query from the URL.

        search_calls_per_query = QUERY_CALLS_LIMIT
        number_of_queries_in_window = 0

        q_submissions = []
        # do as many calls per query as possible
        for _ in range(search_calls_per_query):
            try:
                q_submissions.extend(
                    python_reddit.subreddit(subreddit_name).search(
                        query=search_query, sort=self.arguments.sort, limit=q_count
                    )
                )
                number_of_queries_in_window += 1
            except Exception as e:
                __logger__.error(str(e), extra={"props": {"transformer": self.type}})
                break

        # Loop through all results given (q_count)
        for q_submission in q_submissions:
            submission = {}
            submission["content"] = {}

            submission["content"]["selftext"] = str(q_submission.selftext)
            submission["content"]["subreddit"] = str(q_submission.subreddit)

            submission["title"] = str(q_submission.title)
            submission["origin"] = f"https://www.reddit.com{q_submission.permalink}"

            submissions.append(submission)

        return submissions

    def transform(self, source):
        super().transform(source=source)

        content = []
        subreddit = (
            self.arguments.subreddit if self.arguments.subreddit is not None else "all"
        )
        submissions = self.search_reddit(source, self.arguments.search, subreddit)

        for submission in submissions:
            document = documents.Form.new_from(
                source,
                content=submission["content"],
                origin=submission["origin"],
                title=submission["title"],
            )
            content.append(document)
        title = f"Reddit search for {self.arguments.search} on subreddit {subreddit}"

        return documents.Collection.new_from(None, title=title, content=content)
