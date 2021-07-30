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

import argparse
import tempfile

from ingestum import engine
from ingestum import manifests
from ingestum import pipelines
from ingestum import transformers
from ingestum.utils import stringify_document


def generate_pipeline():
    # Sometimes PDF files contain images of text rather than
    # postscript. This pipeline treats the pages in a PDF as images
    # and extracts the text through OCR.
    pipeline = pipelines.base.Pipeline(
        name="pipeline_ocr",
        pipes=[
            pipelines.base.Pipe(
                name="document",
                sources=[pipelines.sources.Manifest(source="pdf")],
                steps=[
                    # The first step is to run each page of the PDF
                    # through an OCR process.
                    transformers.PDFSourceCreateTextDocumentOCR(
                        first_page=-1, last_page=-1
                    ),
                    # Mark paragraph breaks.
                    transformers.TextDocumentStringReplace(
                        regexp="\\.\\s*\\n", replacement=".PARAGRAPH_BREAK"
                    ),
                    # Split paragraphs into passages.
                    transformers.TextSplitIntoCollectionDocument(
                        separator="PARAGRAPH_BREAK"
                    ),
                    transformers.CollectionDocumentTransform(
                        transformer=transformers.TextCreatePassageDocument()
                    ),
                    # Here we add a tag to indicate that the text came
                    # from OCR.
                    transformers.CollectionDocumentTransform(
                        transformer=transformers.PassageDocumentAddMetadata(
                            key="tags", value="OCR"
                        )
                    ),
                ],
            )
        ],
    )
    return pipeline


def ingest(path, first_page, last_page):
    destination = tempfile.TemporaryDirectory()

    manifest = manifests.base.Manifest(
        sources=[
            manifests.sources.PDF(
                id="id",
                pipeline="pipeline_ocr",
                first_page=first_page,
                last_page=last_page,
                location=manifests.sources.locations.Local(
                    path=path,
                ),
                destination=manifests.sources.destinations.Local(
                    directory=destination.name,
                ),
            )
        ]
    )

    pipeline = generate_pipeline()

    results, _ = engine.run(
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
    ingest_parser.add_argument("path")
    ingest_parser.add_argument("first_page")
    ingest_parser.add_argument("last_page")
    args = parser.parse_args()

    if args.command == "export":
        output = generate_pipeline()
    else:
        output = ingest(args.path, args.first_page, args.last_page)

    print(stringify_document(output))


if __name__ == "__main__":
    main()
