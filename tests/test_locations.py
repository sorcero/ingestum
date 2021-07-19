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

skip_remove_video = os.environ.get("GITLAB_CI") is not None
tmpdir = None


def setup_module():
    global tmpdir
    tmpdir = tempfile.TemporaryDirectory()


def teardown_module():
    tmpdir.cleanup()


def test_local_location():
    location = manifests.sources.locations.Local(path="tests/data/test.txt")
    manifest_source = manifests.sources.Text(id="", pipeline="", location=location)
    source = manifest_source.get_source(tmpdir.name, tmpdir.name)
    assert source is not None
    assert os.path.exists(source.path)


def test_remote_location():
    location = manifests.sources.locations.Remote(
        url="https://gitlab.com/sorcero/community/ingestum/-/raw/master/tests/data/test.pdf?inline=false"
    )
    manifest_source = manifests.sources.PDF(
        id="", pipeline="", first_page=1, last_page=3, location=location
    )
    source = manifest_source.get_source(tmpdir.name, tmpdir.name)
    assert source is not None
    assert os.path.exists(source.path)


@pytest.mark.skipif(skip_remove_video, reason="Skipping for Gitlab CI")
def test_remote_video_location():
    location = manifests.sources.locations.RemoteVideo(
        url="https://vimeo.com/396969664"
    )
    manifest_source = manifests.sources.Audio(id="", pipeline="", location=location)
    source = manifest_source.get_source(tmpdir.name, tmpdir.name)
    assert source is not None
    assert os.path.exists(source.path)


datalake_project = os.environ.get("INGESTUM_GOOGLE_DATALAKE_TEST_PROJECT", None)
datalake_bucket = os.environ.get("INGESTUM_GOOGLE_DATALAKE_TEST_BUCKET", None)
datalake_path = os.environ.get("INGESTUM_GOOGLE_DATALAKE_TEST_PATH", None)
datalake_token = os.environ.get("INGESTUM_GOOGLE_DATALAKE_TEST_TOKEN", None)

skip_google_datalake = (
    not datalake_project
    or not datalake_bucket
    or not datalake_path
    or not datalake_token
)


@pytest.mark.skipif(skip_google_datalake, reason="Skipping for Gitlab CI")
def test_google_datalake_location():
    credential = manifests.sources.locations.credentials.OAuth2(token=datalake_token)
    location = manifests.sources.locations.GoogleDatalake(
        project=datalake_project,
        bucket=datalake_bucket,
        path=datalake_path,
        credential=credential,
    )
    manifest_source = manifests.sources.PDF(
        id="", pipeline="", first_page=1, last_page=3, location=location
    )
    source = manifest_source.get_source(tmpdir.name, tmpdir.name)
    assert source is not None
    assert os.path.exists(source.path)
