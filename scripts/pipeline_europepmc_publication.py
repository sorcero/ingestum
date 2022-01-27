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
        name="pipeline_europepmc",
        pipes=[
            pipelines.base.Pipe(
                name="document",
                sources=[pipelines.sources.Manifest(source="europepmc")],
                steps=[
                    # Connects to the Europe PMC web service API and collects
                    # documents that matches the query parameters
                    transformers.EuropePMCSourceCreatePublicationCollectionDocument(
                        query="",
                        articles=-1,
                        hours=-1,
                        from_date="",
                        to_date="",
                        full_text=False,
                    )
                ],
            )
        ],
    )
    return pipeline


def ingest(query, articles, hours, from_date, to_date, full_text):
    destination = tempfile.TemporaryDirectory()

    manifest = manifests.base.Manifest(
        sources=[
            manifests.sources.EuropePMC(
                id="id",
                pipeline="pipeline_europepmc",
                query=query,
                articles=articles,
                hours=hours,
                from_date=from_date,
                to_date=to_date,
                full_text=full_text,
                destination=manifests.sources.destinations.Local(
                    directory=destination.name
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
    ingest_parser.add_argument("query", type=str)
    ingest_parser.add_argument("articles", type=int)
    ingest_parser.add_argument("--hours", type=int, default=-1)
    ingest_parser.add_argument("--from_date", type=str, default="")
    ingest_parser.add_argument("--to_date", type=str, default="")
    ingest_parser.add_argument("--full_text", type=bool, default=False)
    args = parser.parse_args()

    if args.command == "export":
        output = generate_pipeline()
    else:
        output = ingest(
            args.query,
            args.articles,
            args.hours,
            args.from_date,
            args.to_date,
            args.full_text,
        )

    print(stringify_document(output))


if __name__ == "__main__":
    main()
