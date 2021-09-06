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

import json
import argparse
import tempfile

from ingestum import engine
from ingestum import manifests
from ingestum import pipelines
from ingestum import transformers


def generate_pipeline():
    pipeline = pipelines.base.Pipeline(
        name="pipeline_pdf_hybrid",
        pipes=[
            # Extract all tables from the PDF into
            # a collection.
            pipelines.base.Pipe(
                name="tables",
                sources=[pipelines.sources.Manifest(source="pdf")],
                steps=[
                    transformers.PDFSourceCreateTabularCollectionDocumentHybrid(
                        first_page=-1,
                        last_page=-1,
                    )
                ],
            ),
            # Create a new collection with the Markdown
            # version of each of these tables.
            pipelines.base.Pipe(
                name="tables-replacements",
                sources=[
                    pipelines.sources.Pipe(
                        name="tables",
                    )
                ],
                steps=[
                    transformers.CollectionDocumentTransform(
                        transformer=transformers.TabularDocumentCreateMDPassage()  # noqa: E251
                    )
                ],
            ),
            # Sometimes PDF files contain a combination of PostScript text and
            # images of text. This pipeline uses contour matching to find
            # regions with text and merges PostScript and OCR text.
            pipelines.base.Pipe(
                name="text",
                sources=[
                    pipelines.sources.Manifest(source="pdf"),
                    pipelines.sources.Pipe(name="tables"),
                    pipelines.sources.Pipe(name="tables-replacements"),
                ],
                steps=[
                    transformers.PDFSourceCreateTextDocumentHybridReplacedExtractables(
                        first_page=-1, last_page=-1, layout="multi"
                    ),
                    # Replace ligatures
                    transformers.TextDocumentStringReplace(
                        regexp="æ", replacement="ae"
                    ),
                    transformers.TextDocumentStringReplace(
                        regexp="ﬁ", replacement="fi"
                    ),
                    transformers.TextDocumentStringReplace(
                        regexp="ﬂ", replacement="fl"
                    ),
                    # Mark paragraph breaks.
                    transformers.TextDocumentStringReplace(
                        regexp="\\.\\s*\\n", replacement=".PARAGRAPH_BREAK"
                    ),
                    # Double newlines should be preserved.
                    transformers.TextDocumentStringReplace(
                        regexp="\\n\\n", replacement="DOUBLE_NEWLINE"
                    ),
                    # Dehyphenate.
                    transformers.TextDocumentHyphensRemove(),
                    # Remove the stray new lines.
                    transformers.TextDocumentStringReplace(
                        regexp="\\n", replacement=" "
                    ),
                    # Restore double newlines.
                    transformers.TextDocumentStringReplace(
                        regexp="DOUBLE_NEWLINE", replacement="\\n\\n"
                    ),
                    # Split paragraphs into passages.
                    transformers.TextSplitIntoCollectionDocument(
                        separator="PARAGRAPH_BREAK"
                    ),
                    transformers.CollectionDocumentTransform(
                        transformer=transformers.TextCreatePassageDocument()
                    ),
                    # Here we add a tag to indicate that the text is a mix of
                    # PostScript and OCR text.
                    transformers.CollectionDocumentTransform(
                        transformer=transformers.PassageDocumentAddMetadata(
                            key="tags", value="hybrid"
                        )
                    ),
                ],
            ),
        ],
    )
    return pipeline


def ingest(path, first_page, last_page):
    destination = tempfile.TemporaryDirectory()

    manifest = manifests.base.Manifest(
        sources=[
            manifests.sources.PDF(
                id="id",
                pipeline="pipeline_pdf_hybrid",
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
    ingest_parser.add_argument("path")
    ingest_parser.add_argument("first_page", nargs="?", default=None)
    ingest_parser.add_argument("last_page", nargs="?", default=None)
    args = parser.parse_args()

    if args.command == "export":
        output = generate_pipeline()
    else:
        output = ingest(args.path, args.first_page, args.last_page)

    print(json.dumps(output.dict(), indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
