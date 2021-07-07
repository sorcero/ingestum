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
import sox
import tempfile

from typing_extensions import Literal

from ... import sources
from .located import Source as BaseSource


class Source(BaseSource):

    type: Literal["audio"] = "audio"

    def get_source(self, output_dir, cache_dir):
        # can't use /tmp due to xattr limitations
        raw_output_dir = tempfile.TemporaryDirectory(dir=os.path.expanduser("~"))
        raw_path = self.location.fetch(raw_output_dir.name, cache_dir)

        path = os.path.join(output_dir, "source.wav")
        self.preprocess_audio(raw_path, path)

        raw_output_dir.cleanup()
        return sources.Audio(path=path)

    @staticmethod
    def preprocess_audio(source, dest):
        tfm = sox.Transformer()
        tfm.set_output_format(
            rate=16000, bits=16, channels=1, encoding="signed-integer"
        )
        tfm.build(source, dest)
