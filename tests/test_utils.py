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
import pytest
import requests

from bs4 import BeautifulSoup

from ingestum import sources
from ingestum import utils

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_html_table_to_markdown_table():
    source = sources.HTML(path=os.path.join(ROOT_DIR, "tests/input/html_table.html"))
    with open(source.path) as html:
        content = html.read()

    soup = BeautifulSoup(content, "xml")
    table = utils.html_table_to_markdown_table(soup)

    with open(
        os.path.join(ROOT_DIR, "tests/output/html_table_to_markdown_table.txt")
    ) as f:
        output = "".join(f.readlines())

    assert table == output


def test_create_session_with_default_timeout():
    request = utils.create_request(total=0, default_timeout=1)
    with pytest.raises(requests.exceptions.ConnectionError):
        request.get("https://httpstat.us/200?sleep=40000")
