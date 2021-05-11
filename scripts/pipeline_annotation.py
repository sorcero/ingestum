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
        name="pipeline_annotation",
        pipes=[
            pipelines.base.Pipe(
                name="document",
                sources=[pipelines.sources.Manifest(source="pdf")],
                steps=[
                    # Create a PNG image out of a given rectangle
                    # inside the PDF. In this case, the whole first
                    # page.
                    transformers.PDFSourceCropCreateImageSource(
                        directory="",
                        prefix="",
                        page=1,
                        width=500,
                        height=700,
                        left=0,
                        top=0,
                        right=500,
                        bottom=700,
                    ),
                    # Extract the human-readable text from the image.
                    transformers.ImageSourceCreateTextDocument(),
                    # Create a passage.
                    transformers.TextCreatePassageDocument(),
                    transformers.PassageDocumentAddMetadata(key="tags", value="text"),
                ],
            ),
            pipelines.base.Pipe(
                name="collection",
                sources=[
                    pipelines.sources.Nothing(),
                    pipelines.sources.Pipe(name="document"),
                ],
                steps=[transformers.CollectionDocumentAdd()],
            ),
            pipelines.base.Pipe(
                name="figure",
                sources=[pipelines.sources.Manifest(source="pdf")],
                steps=[
                    # Create a PNG image out of a given rectangle
                    # inside the PDF. In this case, the whole first
                    # page.
                    transformers.PDFSourceCropCreateImageSource(
                        directory="",
                        prefix="figure",
                        page=1,
                        width=500,
                        height=700,
                        left=0,
                        top=0,
                        right=500,
                        bottom=700,
                    ),
                    # Create a text reference (e.g. file:///figure.png)
                    # to the image.
                    transformers.ImageSourceCreateReferenceTextDocument(),
                    transformers.TextCreatePassageDocument(),
                    transformers.PassageDocumentAddMetadata(key="tags", value="figure"),
                ],
            ),
            # Put both passages inside the same collection
            # to keep the output format consistent.
            pipelines.base.Pipe(
                name="collection",
                sources=[
                    pipelines.sources.Pipe(name="collection"),
                    pipelines.sources.Pipe(name="figure"),
                ],
                steps=[transformers.CollectionDocumentAdd()],
            ),
        ],
    )
    return pipeline


def ingest(url, first_page, last_page):
    manifest = manifests.base.Manifest(
        sources=[
            manifests.sources.PDF(
                id="id",
                pipeline="pipeline_annotation",
                first_page=first_page,
                last_page=last_page,
                url=url,
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
    ingest_parser.add_argument("first_page")
    ingest_parser.add_argument("last_page")
    args = parser.parse_args()

    if args.command == "export":
        output = generate_pipeline()
    else:
        output = ingest(args.url, args.first_page, args.last_page)

    print(json.dumps(output.dict(), indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
