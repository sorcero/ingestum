#!/usr/bin/python3
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

import json
import argparse
import tempfile

from ingestum import engine
from ingestum import manifests
from ingestum import pipelines
from ingestum import transformers


def generate_pipeline():
    # Note that this pipeline requires that INGESTUM_REDDIT_CLIENT_ID, and
    # INGESTUM_REDDIT_CLIENT_SECRET be defined in the environment.
    pipeline = pipelines.base.Pipeline(
        name="pipeline_reddit",
        pipes=[
            pipelines.base.Pipe(
                name="search",
                sources=[pipelines.sources.Manifest(source="reddit")],
                steps=[
                    # The Reddit source will take each result of a
                    # Reddit search and add it to a collection of
                    # text documents. From there, additional
                    # transformers can be applied.
                    transformers.RedditSourceCreateFormCollectionDocument(
                        search="", subreddit=""
                    )
                ],
            )
        ],
    )
    return pipeline


def ingest(search, subreddit="all"):
    manifest = manifests.base.Manifest(
        sources=[
            manifests.sources.Reddit(
                id="id", pipeline="pipeline_reddit", search=search, subreddit=subreddit
            )
        ]
    )

    pipeline = generate_pipeline()
    workspace = tempfile.TemporaryDirectory()

    results, _ = engine.run(
        manifest=manifest,
        pipelines=[pipeline],
        pipelines_dir=None,
        artifacts_dir=None,
        workspace_dir=workspace.name,
    )

    workspace.cleanup()

    return results[0]


def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="command", required=True)
    subparser.add_parser("export")
    ingest_parser = subparser.add_parser("ingest")
    ingest_parser.add_argument("search")
    ingest_parser.add_argument("subreddit", nargs="?")
    args = parser.parse_args()

    if args.command == "export":
        output = generate_pipeline()
    else:
        if args.subreddit:
            output = ingest(args.search, args.subreddit)
        else:
            output = ingest(args.search)

    print(json.dumps(output.dict(), indent=4, sort_keys=True))


if __name__ == "__main__":
    main()