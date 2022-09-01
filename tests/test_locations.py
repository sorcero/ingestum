# -*- coding: utf-8 -*-

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

import os
import tempfile
import pytest

from ingestum import manifests

from tests.utils import (
    skip_google_datalake,
    skip_remove_video,
    google_datalake_project,
    google_datalake_bucket,
    google_datalake_path,
    google_datalake_token,
)


def test_local_location():
    outputs = tempfile.TemporaryDirectory()
    artifacts = tempfile.TemporaryDirectory()
    destinations = tempfile.TemporaryDirectory()

    location = manifests.sources.locations.Local(path="tests/data/test.txt")
    destination = manifests.sources.destinations.Local(directory=destinations.name)

    manifest_source = manifests.sources.Text(
        id="",
        pipeline="",
        location=location,
        destination=destination,
    )
    source = manifest_source.get_source(outputs.name, artifacts.name)

    assert source is not None
    assert os.path.exists(source.path)

    outputs.cleanup()
    artifacts.cleanup()
    destinations.cleanup()


def test_remote_location():
    outputs = tempfile.TemporaryDirectory()
    artifacts = tempfile.TemporaryDirectory()
    destinations = tempfile.TemporaryDirectory()

    location = manifests.sources.locations.Remote(
        url="https://gitlab.com/sorcero/community/ingestum/-/raw/master/tests/data/test.pdf?inline=false"
    )
    destination = manifests.sources.destinations.Local(directory=destinations.name)

    manifest_source = manifests.sources.PDF(
        id="",
        pipeline="",
        first_page=1,
        last_page=3,
        location=location,
        destination=destination,
    )
    source = manifest_source.get_source(outputs.name, artifacts.name)

    assert source is not None
    assert os.path.exists(source.path)
    assert os.path.basename(source.path) == "source.pdf"

    outputs.cleanup()
    artifacts.cleanup()
    destinations.cleanup()


@pytest.mark.skipif(skip_remove_video, reason="Skipping for Gitlab CI")
def test_remote_video_location():
    outputs = tempfile.TemporaryDirectory()
    artifacts = tempfile.TemporaryDirectory()
    destinations = tempfile.TemporaryDirectory()

    location = manifests.sources.locations.RemoteVideo(
        url="https://vimeo.com/396969664"
    )
    destination = manifests.sources.destinations.Local(directory=destinations.name)

    manifest_source = manifests.sources.Audio(
        id="",
        pipeline="",
        location=location,
        destination=destination,
    )
    source = manifest_source.get_source(outputs.name, artifacts.name)

    assert source is not None
    assert os.path.exists(source.path)

    outputs.cleanup()
    artifacts.cleanup()
    destinations.cleanup()


@pytest.mark.skipif(skip_google_datalake, reason="Skipping for Gitlab CI")
def test_google_datalake_location():
    outputs = tempfile.TemporaryDirectory()
    artifacts = tempfile.TemporaryDirectory()
    destinations = tempfile.TemporaryDirectory()

    credential = manifests.sources.credentials.OAuth2(token=google_datalake_token)
    location = manifests.sources.locations.GoogleDatalake(
        project=google_datalake_project,
        bucket=google_datalake_bucket,
        path=google_datalake_path,
        credential=credential,
    )
    destination = manifests.sources.destinations.Local(directory=destinations.name)

    manifest_source = manifests.sources.PDF(
        id="",
        pipeline="",
        first_page=1,
        last_page=3,
        location=location,
        destination=destination,
    )
    source = manifest_source.get_source(outputs.name, artifacts.name)

    assert source is not None
    assert os.path.exists(source.path)

    outputs.cleanup()
    artifacts.cleanup()
    destinations.cleanup()
