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


import unittest

from ingestum import sources
from ingestum import transformers

from tests import utils


class AudioTestCase(unittest.TestCase):

    audio_source = sources.Audio(path="tests/data/test.wav")

    def test_audio_source_create_text_document(self):
        source = self.audio_source
        document = transformers.AudioSourceCreateTextDocument().transform(source=source)
        self.assertEqual(
            document.dict(), utils.get_expected("audio_source_create_text_document")
        )


if __name__ == "__main__":
    unittest.main()
