# -*- coding: utf-8 -*-

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


import os
import json
import copy
import uuid
import pathlib
import shutil

from ingestum import pipelines
from ingestum import transformers

DEFAULT_DOC = "document.json"


def prepare_transformer(source, transformer, output_directory):
    for attribute in transformer.arguments.__dict__.keys():
        value = getattr(transformer.arguments, attribute)
        if isinstance(value, transformers.base.BaseTransformer):
            prepare_transformer(source, value, output_directory)
            continue
        if hasattr(source, attribute) and value == getattr(
            source, f"{attribute}_placeholder"
        ):
            setattr(transformer.arguments, attribute, getattr(source, attribute))
        # XXX make sure directories ARE contained in workspace
        if attribute == "directory":
            transformer.arguments.directory = output_directory


def prepare_pineline(source, pipeline, output_directory):
    for pipe in pipeline.pipes:
        for transformer in pipe.steps:
            prepare_transformer(source, transformer, output_directory)


def find_pipeline(source, _pipelines, pipelines_dir, output_directory):
    pipeline = None

    if _pipelines is not None:
        pipeline = next(
            (p for p in _pipelines if source.pipeline == p.name), None
        )  # noqa: E501
        pipeline = copy.deepcopy(pipeline) if pipeline else None

    if pipeline is None and pipelines_dir is not None:
        pipeline_path = os.path.join(pipelines_dir, f"{source.pipeline}.json")
        pipeline = pipelines.Base.parse_file(pipeline_path)

    if pipeline is not None:
        prepare_pineline(source, pipeline, output_directory)

    return pipeline


def artifactify(output_directory, artifacts_dir):
    if artifacts_dir is None:
        return None

    name = str(uuid.uuid4())
    zip_path = os.path.join(artifacts_dir, name)
    shutil.make_archive(zip_path, "zip", output_directory)

    return name


def store(document, output_directory):
    document_path = os.path.join(output_directory, DEFAULT_DOC)
    with open(document_path, "w") as document_file:
        document_file.write(json.dumps(document.dict(), indent=4, sort_keys=True))


def run(manifest, pipelines, pipelines_dir, artifacts_dir, workspace_dir):
    documents = []
    artifacts = []

    cache_directory = os.path.join(workspace_dir, "cache")
    pathlib.Path(cache_directory).mkdir(parents=True, exist_ok=True)

    for source in manifest.sources:

        source_directory = os.path.join(workspace_dir, source.id)
        pathlib.Path(source_directory).mkdir(parents=True, exist_ok=True)

        output_directory = os.path.join(source_directory, "output")
        pathlib.Path(output_directory).mkdir(parents=True, exist_ok=True)

        pipeline = find_pipeline(
            source, pipelines, pipelines_dir, output_directory
        )  # noqa: E501
        document = pipeline.run(source_directory, source, cache_directory)

        store(document, output_directory)
        artifact = artifactify(output_directory, artifacts_dir)

        documents.append(document)
        artifacts.append(artifact)

    return documents, artifacts
