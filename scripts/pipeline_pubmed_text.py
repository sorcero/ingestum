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
    pipeline = pipelines.base.Pipeline(
        name="pipeline_pubmed",
        pipes=[
            pipelines.base.Pipe(
                name="document",
                sources=[pipelines.sources.Manifest(source="pubmed")],
                steps=[
                    # Connects to PubMed web service API and collects
                    # documents that matches the terms
                    transformers.PubmedSourceCreateTextCollectionDocument(
                        articles=-1,
                        hours=-1,
                        terms=[],
                    )
                ],
            )
        ],
    )
    return pipeline


def ingest(articles, hours, terms):
    destination = tempfile.TemporaryDirectory()

    manifest = manifests.base.Manifest(
        sources=[
            manifests.sources.PubMed(
                id="id",
                pipeline="pipeline_pubmed",
                terms=terms,
                hours=hours,
                articles=articles,
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
    ingest_parser.add_argument("articles", type=int)
    ingest_parser.add_argument("hours", type=int)
    ingest_parser.add_argument("terms", nargs="+")
    args = parser.parse_args()

    if args.command == "export":
        output = generate_pipeline()
    else:
        output = ingest(args.articles, args.hours, args.terms)

    print(stringify_document(output))


if __name__ == "__main__":
    main()
