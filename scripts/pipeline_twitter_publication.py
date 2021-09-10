#!/usr/bin/python3
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

import argparse
import tempfile

from ingestum import engine
from ingestum import manifests
from ingestum import pipelines
from ingestum import transformers
from ingestum.utils import stringify_document


def generate_pipeline():
    # Note that this pipeline requires that INGESTUM_TWITTER_CONSUMER_KEY, and
    # INGESTUM_TWITTER_CONSUMER_SECRET be defined in the environment.
    pipeline = pipelines.base.Pipeline(
        name="pipeline_twitter",
        pipes=[
            pipelines.base.Pipe(
                name="search",
                sources=[pipelines.sources.Manifest(source="twitter")],
                steps=[
                    # The twitter source will take each result of a
                    # twitter search and add it to a collection of
                    # publication documents. From there, additional
                    # transformers can be applied.
                    transformers.TwitterSourceCreatePublicationCollectionDocument(
                        search="", count=-1, sort="", tags=[]
                    )
                ],
            )
        ],
    )
    return pipeline


def ingest(search, count, sort, tags):
    destination = tempfile.TemporaryDirectory()

    manifest = manifests.base.Manifest(
        sources=[
            manifests.sources.Twitter(
                id="id",
                pipeline="pipeline_twitter",
                search=search,
                count=count,
                sort=sort,
                tags=tags,
                destination=manifests.sources.destinations.Local(
                    directory=destination.name,
                ),
            )
        ]
    )

    pipeline = generate_pipeline()

    results, *_ = engine.run(
        manifest=manifest,
        pipelines=[pipeline],
        pipelines_dir=None,
        artifacts_dir=None,
        workspace_dir=None,
    )

    destination.cleanup()

    return results[0]


def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="command", required=True)
    subparser.add_parser("export")
    ingest_parser = subparser.add_parser("ingest")
    ingest_parser.add_argument("search", type=str)
    ingest_parser.add_argument("count", type=int)
    ingest_parser.add_argument("sort", type=str)
    ingest_parser.add_argument("tags", nargs="*", type=str, default=[])
    args = parser.parse_args()

    if args.command == "export":
        output = generate_pipeline()
    else:
        output = ingest(args.search, args.count, args.sort, args.tags)

    print(stringify_document(output))


if __name__ == "__main__":
    main()
