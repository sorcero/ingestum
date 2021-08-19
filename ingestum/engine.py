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
import copy
import pathlib
import tempfile

from ingestum import pipelines
from ingestum import transformers
from ingestum import workers


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


def run_source(
    source, pipelines, pipelines_dir, cache_dir, artifacts_dir, workspace_dir
):
    source_directory = os.path.join(workspace_dir, source.id)
    pathlib.Path(source_directory).mkdir(parents=True, exist_ok=True)

    output_directory = os.path.join(source_directory, "output")
    pathlib.Path(output_directory).mkdir(parents=True, exist_ok=True)

    pipeline = find_pipeline(
        source, pipelines, pipelines_dir, output_directory
    )  # noqa: E501
    document = pipeline.run(source_directory, source, cache_dir)
    location = source.destination.store(document, output_directory, artifacts_dir)

    return document, location


def run(manifest, pipelines, pipelines_dir, artifacts_dir=None, workspace_dir=None):
    documents = []
    locations = []

    # Allow our API clients to not-have to provide any filesystem-specific data
    if artifacts_dir is None:
        artifacts_tmp = tempfile.TemporaryDirectory()
        artifacts_dir = artifacts_tmp.name
    if workspace_dir is None:
        workspace_tmp = tempfile.TemporaryDirectory()
        workspace_dir = workspace_tmp.name

    cache_dir = os.path.join(workspace_dir, "cache")
    pathlib.Path(cache_dir).mkdir(parents=True, exist_ok=True)

    worker = workers.get_active_worker()
    results = worker.run(
        manifest.sources,
        run_source,
        pipelines,
        pipelines_dir,
        workspace_dir=workspace_dir,
        artifacts_dir=artifacts_dir,
        cache_dir=cache_dir,
    )

    for result in results:
        document, location = result
        documents.append(document)
        locations.append(location)

    if "artifacts_tmp" in locals():
        artifacts_tmp.cleanup()
    if "workspace_tmp" in locals():
        workspace_tmp.cleanup()

    return documents, locations
