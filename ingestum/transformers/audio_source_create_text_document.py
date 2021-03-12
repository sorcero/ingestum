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
import numpy as np
import wave

from deepspeech import Model
from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from .. import sources
from .base import BaseTransformer, WrongTransformerInput

__script__ = os.path.basename(__file__).replace(".py", "")

DATA_DIR_DEFAULT = os.path.join(os.path.expanduser("~"), ".deepspeech")
DATA_DIR = os.environ.get("INGESTUM_DEEPSPEECH_DIR", DATA_DIR_DEFAULT)
MODEL_PATH = os.path.join(DATA_DIR, "models.pbmm")
SCORER_PATH = os.path.join(DATA_DIR, "models.scorer")


class Transformer(BaseTransformer):
    """
    Transforms an Audio source into a Text document where
    the text document contains the transcript of the audio.
    """

    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        source: sources.Audio

    class OutputsModel(BaseModel):
        document: documents.Text

    type: Literal[__script__] = __script__
    arguments: Optional[ArgumentsModel]
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    @staticmethod
    def extract(source):
        ds = Model(MODEL_PATH)
        ds.enableExternalScorer(SCORER_PATH)
        ds_rate = ds.sampleRate()

        fin = wave.open(str(source.path), "rb")
        fin_audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)
        fin_rate = fin.getframerate()
        fin.close()

        if fin_rate != ds_rate:
            raise WrongTransformerInput("Audio requires %s Hz" % ds_rate)

        return ds.stt(fin_audio)

    def transform(self, source):
        super().transform(source=source)

        return documents.Text.new_from(source, content=self.extract(source))
