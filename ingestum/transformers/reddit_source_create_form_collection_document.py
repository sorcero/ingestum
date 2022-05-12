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
import logging

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from .. import sources
from .base import BaseTransformer

__logger__ = logging.getLogger("ingestum")
__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a `Reddit` source into a `Collection` of `Form` documents with
    the submissions of a subreddit.

    :param search: The search string to pass to a Reddit query, e.g., "python"
        https://www.reddit.com/search/?q=python
    :type search: str
    :param subreddit: Limit search results to the subreddit if provided
    :type subreddit: str
    :param sort: The sorting criteria for the search
        The options are: ``"relevance"``, ``"hot"``, ``"new"``, ``"top"``,
        ``"comments"``; defaults to ``"relevance"``
    :type sort: str
    :param count: The number of results to try and retrieve (defaults to 100)
    :type count: Optional[int]
    """

    class ArgumentsModel(BaseModel):
        search: str
        subreddit: Optional[str] = "all"
        sort: Optional[str] = "relevance"
        count: Optional[int] = 100

    class InputsModel(BaseModel):
        source: sources.Reddit

    class OutputsModel(BaseModel):
        document: documents.Collection

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def search_reddit(self, source, search_query, subreddit_name):
        # Get Reddit instance.
        python_reddit = source.get_reddit()

        # Generate queries.
        q_count = min(self.arguments.count, 100)  # max allowed per query

        q_submissions = []
        try:
            q_submissions.extend(
                python_reddit.subreddit(subreddit_name).search(
                    query=search_query, sort=self.arguments.sort, limit=q_count
                )
            )
        except Exception as e:
            __logger__.error(str(e), extra={"props": {"transformer": self.type}})

        return q_submissions

    def get_document(self, source, post):
        submission = {}
        submission["content"] = {}

        submission["content"]["selftext"] = str(post.selftext)
        submission["content"]["subreddit"] = str(post.subreddit)

        submission["title"] = str(post.title)
        submission["origin"] = f"https://www.reddit.com{post.permalink}"

        return documents.Form.new_from(source, **submission)

    def transform(self, source: sources.Reddit) -> documents.Collection:
        super().transform(source=source)

        content = []
        subreddit = (
            self.arguments.subreddit if self.arguments.subreddit is not None else "all"
        )
        submissions = self.search_reddit(source, self.arguments.search, subreddit)

        for submission in submissions:
            document = self.get_document(source, submission)
            content.append(document)
        title = f"Reddit search for {self.arguments.search} on subreddit {subreddit}"

        return documents.Collection.new_from(
            None, title=title, content=content, context=self.context(exclude=["search"])
        )
