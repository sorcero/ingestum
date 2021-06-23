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
import sys
import inspect
import logging

from pydantic import BaseModel
from typing_extensions import Literal

__logger__ = logging.getLogger("ingestum")

PLUGINS_DIR = os.path.join(os.path.expanduser("~"), ".ingestum", "plugins")
IGNORE_LIST = [
    ".git",
    "env",
]


class Manager(BaseModel):
    type: Literal["manager"] = "manager"
    directory: str = os.environ.get("INGESTUM_PLUGINS_DIR", PLUGINS_DIR)

    def register(self, module, concept_name, concept_class):
        if not os.path.exists(self.directory):
            return

        if self.directory not in sys.path:
            sys.path.append(self.directory)

        for plugin in os.listdir(self.directory):
            path_to_concept = concept_name.replace(".", "/")
            if plugin in IGNORE_LIST or not os.path.isdir(
                os.path.join(self.directory, plugin, path_to_concept)
            ):
                continue

            try:
                plugin_import = f"{plugin}.{concept_name}"
                __logger__.debug(
                    "loading",
                    extra={"props": {"plugin": plugin, "concept": concept_name}},
                )
                plugin_module = __import__(plugin_import)
            except ImportError as e:
                __logger__.debug(str(e), extra={"props": {"plugin": plugin}})
                continue

            for component in concept_name.split("."):
                plugin_module = getattr(plugin_module, component)

            for name in dir(plugin_module):
                if name.startswith("__"):
                    continue

                class_ = getattr(plugin_module, name)
                if not inspect.isclass(class_):
                    continue

                if issubclass(class_, concept_class):
                    setattr(module, name, class_)


default = Manager()
