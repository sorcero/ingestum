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


import json
import os


def get_expected(transformer):
    filepath = "tests/output/" + transformer + ".json"
    with open(filepath, "r") as f:
        expected = json.loads(f.read())
    return expected


skip_email = (
    os.environ.get("INGESTUM_EMAIL_HOST") is None
    or os.environ.get("INGESTUM_EMAIL_PORT") is None
    or os.environ.get("INGESTUM_EMAIL_USER") is None
    or os.environ.get("INGESTUM_EMAIL_PASSWORD") is None
)

skip_proquest = (
    os.environ.get("INGESTUM_PROQUEST_ENDPOINT") is None
    or os.environ.get("INGESTUM_PROQUEST_TOKEN") is None
)

skip_pubmed = (
    os.environ.get("INGESTUM_PUBMED_TOOL") is None
    or os.environ.get("INGESTUM_PUBMED_EMAIL") is None
)

skip_reddit = (
    os.environ.get("INGESTUM_REDDIT_CLIENT_ID") is None
    or os.environ.get("INGESTUM_REDDIT_CLIENT_SECRET") is None
)

skip_twitter = (
    os.environ.get("INGESTUM_TWITTER_CONSUMER_KEY") is None
    or os.environ.get("INGESTUM_TWITTER_CONSUMER_SECRET") is None
    or os.environ.get("INGESTUM_TWITTER_ACCESS_TOKEN") is None
    or os.environ.get("INGESTUM_TWITTER_ACCESS_SECRET") is None
)


google_datalake_project = os.environ.get("INGESTUM_GOOGLE_DATALAKE_TEST_PROJECT")
google_datalake_bucket = os.environ.get("INGESTUM_GOOGLE_DATALAKE_TEST_BUCKET")
google_datalake_path = os.environ.get("INGESTUM_GOOGLE_DATALAKE_TEST_PATH")
google_datalake_token = os.environ.get("INGESTUM_GOOGLE_DATALAKE_TEST_TOKEN")

skip_google_datalake = (
    not google_datalake_project
    or not google_datalake_bucket
    or not google_datalake_path
    or not google_datalake_token
)

skip_remove_video = os.environ.get("GITLAB_CI") is not None

skip_remote_destination = not os.environ.get("INGESTUM_TEST_REMOTE_URL")

skip_biorxiv = (
    os.environ.get("INGESTUM_BIORXIV_SEARCH_URL") is None
    or os.environ.get("INGESTUM_BIORXIV_CONTENT_URL") is None
)
skip_medrxiv = (
    os.environ.get("INGESTUM_MEDRXIV_SEARCH_URL") is None
    or os.environ.get("INGESTUM_MEDRXIV_CONTENT_URL") is None
)

skip_europepmc = (
    os.environ.get("INGESTUM_EUROPEPMC_SEARCH_ENDPOINT") is None
    or os.environ.get("INGESTUM_EUROPEPMC_ARTICLE_ENDPOINT") is None
)
