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
    pipeline = pipelines.base.Pipeline(
        name="pipeline_email",
        pipes=[
            pipelines.base.Pipe(
                name="document",
                sources=[pipelines.sources.Manifest(source="email")],
                steps=[
                    # Connects to a email server and searches for
                    # emails received during the last <hours> from
                    # <sender>. See installation docs for necessary
                    # environment variables.
                    transformers.EmailSourceCreateTextCollectionDocument(
                        hours=-1, sender="", subject="", body=""
                    ),
                    transformers.CollectionDocumentTransform(
                        transformer=transformers.TextCreatePassageDocument()
                    ),
                    transformers.CollectionDocumentTransform(
                        transformer=transformers.PassageDocumentAddMetadata(
                            key="tags", value="email"
                        )
                    ),
                ],
            )
        ],
    )
    return pipeline


def ingest(hours, sender, subject, body):
    manifest = manifests.base.Manifest(
        sources=[
            manifests.sources.Email(
                id="id",
                pipeline="pipeline_email",
                hours=hours,
                sender=sender,
                subject=subject,
                body=body,
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
    ingest_parser.add_argument("--hours", type=int, default=24)
    ingest_parser.add_argument("--sender", default="")
    ingest_parser.add_argument("--subject", default="")
    ingest_parser.add_argument("--body", default="")
    args = parser.parse_args()

    if args.command == "export":
        output = generate_pipeline()
    else:
        output = ingest(args.hours, args.sender, args.subject, args.body)

    print(json.dumps(output.dict(), indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
