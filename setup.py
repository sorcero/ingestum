#
# Copyright (c) 2020,2021 Sorcero, Inc.
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

from os import path
from setuptools import setup, find_packages


__path__ = path.abspath(path.dirname(__file__))
with open(path.join(__path__, "requirements.txt")) as f:
    required = f.read().splitlines()


setup(
    name="ingestum",
    version="2.14.0",
    description="Building blocks for document ingestion",
    url="https://gitlab.com/sorcero/community/ingestum",
    author="Sorcero, Inc.",
    author_email="ingestum@sorcero.com",
    packages=find_packages(),
    install_requires=required,
    scripts=[
        "tools/ingestum-pipeline",
        "tools/ingestum-inspect",
        "tools/ingestum-manifest",
        "tools/ingestum-merge",
        "tools/ingestum-migrate",
        "tools/ingestum-generate-manifest",
        "tools/ingestum-generate-manifest-from-xls",
        "tools/ingestum-envelope",
        "tools/ingestum-install-plugins",
    ],
    zip_safe=False,
    python_requires=">=3.7",
)
