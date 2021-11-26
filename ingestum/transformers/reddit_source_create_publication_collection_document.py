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

from typing_extensions import Literal
from datetime import datetime

from .. import documents
from .. import sources
from .reddit_source_create_form_collection_document import (
    Transformer as BaseRedditTransformer,
)
from ..utils import date_to_default_format

__logger__ = logging.getLogger("ingestum")
__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseRedditTransformer):
    """
    Transforms a `Reddit` source into a `Collection` of `Publication`
    documents with the submissions of a subreddit.

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

    type: Literal[__script__] = __script__

    def get_author(self, author):
        return [documents.publication.Author(name=author)]

    def get_publication_date(self, created_utc):
        return date_to_default_format(datetime.fromtimestamp(created_utc))

    def get_publication_type(self, post):
        publication_type = []

        if post.is_self is True:
            publication_type.append("selfpost")

        if "post_hint" in dir(post):
            publication_type.append(str(post.post_hint))
        return publication_type

    def get_document(self, source, post):
        submission = {}

        submission["content"] = str(post.selftext)

        submission["title"] = str(post.title)
        submission["origin"] = f"https://www.reddit.com{post.permalink}"

        submission["authors"] = self.get_author(str(post.author))
        submission["keywords"] = [str(post.subreddit)]
        submission["provider"] = "reddit"
        submission["provider_id"] = str(post.id)
        submission["publication_date"] = self.get_publication_date(post.created_utc)
        submission["publication_type"] = self.get_publication_type(post)

        submission["context"] = {}
        submission["context"]["subreddit"] = str(post.subreddit)
        submission["context"]["upvotes"] = str(post.ups)
        submission["context"]["downvotes"] = str(post.downs)

        return documents.Publication.new_from(source, **submission)

    def transform(self, source: sources.Reddit) -> documents.Collection:
        return super().transform(source=source)
