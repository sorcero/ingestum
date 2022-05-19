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

import os
import subprocess
import sys

from setuptools import setup, find_packages
from setuptools.command.install import install

PLUGINS_DEFAULT_DIR = os.path.join(os.path.expanduser("~"), ".ingestum", "plugins")
PLUGINS_DIRS = os.environ.get("INGESTUM_PLUGINS_DIR", PLUGINS_DEFAULT_DIR).split(":")


class PipInstallAndInstall(install):
    def pip_install(self, name):
        realpath = os.path.realpath(__file__)
        dirname = os.path.dirname(realpath)
        requirements = os.path.join(dirname, name)

        if not os.path.exists(requirements):
            return

        args = [sys.executable, "-m", "pip", "install", "-r", requirements]
        subprocess.check_call(args)

    def plugin_find(self):
        for directory in PLUGINS_DIRS:
            self.plugin_pip_install(directory)

    def plugin_pip_install(self, directory):
        if not os.path.exists(directory):
            return
        for plugin in os.listdir(directory):
            requirements_path = os.path.join(directory, plugin, "requirements.txt")
            self.pip_install(requirements_path)

    def run(self):
        self.pip_install("requirements.txt")
        self.plugin_find()
        install.run(self)


setup(
    name="ingestum",
    version="2.2.0",
    description="Building blocks for document ingestion",
    url="https://gitlab.com/sorcero/community/ingestum",
    author="Sorcero, Inc.",
    author_email="ingestum@sorcero.com",
    packages=find_packages(),
    scripts=[
        "tools/ingestum-pipeline",
        "tools/ingestum-inspect",
        "tools/ingestum-manifest",
        "tools/ingestum-merge",
        "tools/ingestum-migrate",
        "tools/ingestum-generate-manifest",
    ],
    zip_safe=False,
    python_requires=">=3.7",
    cmdclass={
        "install": PipInstallAndInstall,
    },
)
