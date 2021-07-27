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

from ingestum import utils
from ingestum import manifests

from tests.utils import (
    skip_google_datalake,
    skip_remote_destination,
    google_datalake_project,
    google_datalake_bucket,
    google_datalake_path,
    google_datalake_token,
)


def test_local_destination():
    outputs = tempfile.TemporaryDirectory()
    artifacts = tempfile.TemporaryDirectory()
    destinations = tempfile.TemporaryDirectory()

    document = utils.get_document_from_path("tests/input/text_document.json")

    destination = manifests.sources.destinations.Local(directory=destinations.name)
    location = destination.store(document, outputs.name, artifacts.name)

    assert os.path.exists(location.path)

    outputs.cleanup()
    artifacts.cleanup()
    destinations.cleanup()


@pytest.mark.skipif(skip_remote_destination, reason="")
def test_remote_destination():
    outputs = tempfile.TemporaryDirectory()
    artifacts = tempfile.TemporaryDirectory()

    url = os.environ.get("INGESTUM_TEST_REMOTE_URL")
    document = utils.get_document_from_path("tests/input/text_document.json")

    destination = manifests.sources.destinations.Remote(url=url)
    location = destination.store(document, outputs.name, artifacts.name)

    assert location is not None
    assert location.url is not None

    outputs.cleanup()
    artifacts.cleanup()


@pytest.mark.skipif(skip_google_datalake, reason="")
def test_google_datalake_destination():
    outputs = tempfile.TemporaryDirectory()
    artifacts = tempfile.TemporaryDirectory()

    document = utils.get_document_from_path("tests/input/text_document.json")

    credential = manifests.sources.credentials.OAuth2(token=google_datalake_token)
    destination = manifests.sources.destinations.GoogleDatalake(
        prefix="test",
        project=google_datalake_project,
        bucket=google_datalake_bucket,
        path=google_datalake_path,
        credential=credential,
    )

    location = destination.store(document, outputs.name, artifacts.name)

    assert location is not None

    outputs.cleanup()
    artifacts.cleanup()
