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
        name="pipeline_audio",
        pipes=[
            pipelines.base.Pipe(
                name="document",
                sources=[pipelines.sources.Manifest(source="audio")],
                steps=[
                    # An audio source, e.g. WAV. We also extract the
                    # audio from video sources.
                    transformers.AudioSourceCreateTextDocument(),
                    # Once the audio is transcribed, we can process it
                    # like any other text document. Note that the
                    # transcript does not have much in the way of
                    # punctuation.
                    transformers.TextCreatePassageDocument(),
                    # In this example, we add a tag to indicate that
                    # these passages were extracted from audio.
                    transformers.PassageDocumentAddMetadata(key="tags", value="audio"),
                ],
            ),
            pipelines.base.Pipe(
                name="nothing",
                sources=[
                    pipelines.sources.Nothing(),
                    pipelines.sources.Pipe(name="document"),
                ],
                steps=[transformers.CollectionDocumentAdd()],
            ),
        ],
    )
    return pipeline


def ingest(path):
    destination = tempfile.TemporaryDirectory()

    manifest = manifests.base.Manifest(
        sources=[
            manifests.sources.Audio(
                id="id",
                pipeline="pipeline_audio",
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
    args = parser.parse_args()

    if args.command == "export":
        output = generate_pipeline()
    else:
        output = ingest(args.path)

    print(json.dumps(output.dict(), indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
