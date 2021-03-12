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
from typing import Optional, List
from typing_extensions import Literal

from .. import documents
from .. import sources
from .base import BaseTransformer

__logger__ = logging.getLogger("ingestum")
__script__ = os.path.basename(__file__).replace(".py", "")

# Since there are limits to GET calls to Twitter API, we need to make
# sure we do not exceed them.
# https://developer.twitter.com/en/docs/basics/rate-limits
# QUERY_CALLS_LIMIT = 450
QUERY_CALLS_LIMIT = 1


class Transformer(BaseTransformer):
    """
    Transforms a Twitter source into a Collection of Form
    documents with the result of the search.

    Parameters
    ----------
    search : str
        The search string to pass to a twitter query, e.g., Epiduo
        https://twitter.com/search?q=Epiduo
    tags : list
        The list of tags to pull from each tweet
    """

    class ArgumentsModel(BaseModel):
        search: str
        tags: Optional[List[str]]

    class InputsModel(BaseModel):
        source: sources.Twitter

    class OutputsModel(BaseModel):
        document: documents.Collection

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def search_twitter(self, source, search_string):
        tweets = []

        # Get Twython instantiate.
        python_tweets = source.get_feed()

        # Generate queries.
        q_count = 100  # max allowed per query
        # Pull the query from the URL.
        query = {"q": search_string, "result_type": "recent", "count": q_count}

        search_calls_per_query = QUERY_CALLS_LIMIT
        number_of_queries_in_window = 0

        q_statuses = []
        # do as many calls per query as possible
        for _ in range(search_calls_per_query):
            try:
                q_statuses.extend(python_tweets.search(**query)["statuses"])
                number_of_queries_in_window += 1
            except Exception as e:
                __logger__.error(f"{__name__} %s", e)
                break

        tags = self.arguments.tags if self.arguments.tags is not None else ["text"]

        # Loop through all results given (q_count)
        for status in q_statuses:
            tweet = {}
            for tag in tags:
                tweet[tag] = status[tag]
            tweets.append(tweet)

        return tweets

    def transform(self, source):
        super().transform(source=source)

        content = []
        tweets = self.search_twitter(source, self.arguments.search)

        for tweet in tweets:
            data = {
                "title": "",
                "content": tweet,
            }
            document = documents.Form.parse_obj(data)
            content.append(document)

        title = "Twitter search for %s" % self.arguments.search

        return documents.Collection.new_from(None, title=title, content=content)
