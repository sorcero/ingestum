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
        name="pipeline_html",
        pipes=[
            # The first pipeline finds text and images in the HTML
            # content.
            pipelines.base.Pipe(
                name="document",
                sources=[pipelines.sources.Manifest(source="html")],
                steps=[
                    transformers.HTMLSourceCreateDocument(target=""),
                    # We extract the images that are referenced in the
                    # text.
                    transformers.HTMLDocumentImagesExtract(directory="", url=""),
                    # Note: HTML is a subset of XML and we use a
                    # 'xml' encoder with Beautiful Soup, which is case
                    # sensitive, whereas HTML tags are typically
                    # case-insensitive.
                    transformers.XMLCreateTextDocument(),
                    # From here, we can treat the text like any other
                    # text document.
                    transformers.TextCreatePassageDocument(),
                    transformers.PassageDocumentAddMetadata(key="tags", value="html"),
                ],
            ),
            # This pipeline simply takes the pieces extracted above
            # and puts them into one collection.
            pipelines.base.Pipe(
                name="output",
                sources=[
                    pipelines.sources.Nothing(),
                    pipelines.sources.Pipe(name="document"),
                ],
                steps=[transformers.CollectionDocumentAdd()],
            ),
        ],
    )

    return pipeline


def ingest(url, target):
    manifest = manifests.base.Manifest(
        sources=[
            manifests.sources.HTML(
                id="id", pipeline="pipeline_html", url=url, target=target
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
    ingest_parser.add_argument("url")
    ingest_parser.add_argument("target")
    args = parser.parse_args()

    if args.command == "export":
        output = generate_pipeline()
    else:
        output = ingest(args.url, args.target)

    print(json.dumps(output.dict(), indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
