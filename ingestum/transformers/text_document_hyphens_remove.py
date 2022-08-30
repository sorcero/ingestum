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
import logging

import nltk
from nltk.corpus import words

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from .. import documents
from .base import BaseTransformer

__logger__ = logging.getLogger("ingestum")
__script__ = os.path.basename(__file__).replace(".py", "")

NLTK_DATA_DIR_DEFAULT = os.path.join(os.path.expanduser("~"), "nltk_data")
NLTK_DATA = os.environ.get("NLTK_DATA", NLTK_DATA_DIR_DEFAULT)
EN_DICTIONARY_PATH = os.path.join(NLTK_DATA, "corpora", "words", "en")


class Transformer(BaseTransformer):
    """
    Transforms a `Text` document with words separated by hyphens into another
    `Text` document where the hyphens are removed and replaced by words put back
    together.
    """

    class ArgumentsModel(BaseModel):
        pass

    class InputsModel(BaseModel):
        document: documents.Text

    class OutputsModel(BaseModel):
        document: documents.Text

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    dictionary = []

    type: Literal[__script__] = __script__

    def strip_text(self, text):
        """
        Remove common HTML tags and some punctuation.
        """
        text = (
            text.replace("<strong>", "")
            .replace("</strong>", "")
            .replace("<em>", "")
            .replace("</em>", "")
            .replace("<sub>", "")
            .replace("</sub>", "")
            .replace("<sup>", "")
            .replace("</sup>", "")
        )
        text = (
            text.replace("(", "")
            .replace(")", "")
            .replace("[", "")
            .replace("]", "")
            .replace("/", "")
            .replace(",", ".")  # So we can split the text on .
            .replace(";", ".")  # So we can split the text on .
        )
        return text.split(".")[0]

    def simple_present(self, past):
        """
        Simple past to present.
        """
        # This could be improved.
        if past.endswith(("nted", "lled", "cted", "rted", "sted")):
            return past.rstrip("ed")
        if past.endswith("ed"):
            return past.rstrip("d")
        return past

    def simple_singular(self, plural):
        """
        Handles many simple cases.
        armies -> army
        ants -> ant
        accesses -> access
        """
        if plural.endswith("ies"):
            return plural[0:-3] + "y"
        if plural.endswith("ses"):
            return plural[0:-2]
        if plural.endswith("s"):
            return plural.rstrip("s")
        return plural

    def dehyphenate(self, content):
        # Unicode "soft hyphen" is dropped so we need to swap in a hyphen.
        # From there, we make a line list.
        content = content.replace("\u00ad", "-")
        content = content.replace("-\n", "-")
        lines = content.split("\n")
        # Reset content
        content = ""

        # First, make a dictionary of words from the document,
        wlist = []
        # and a list of hypenated words,
        hlist = []
        # and a list of words we will dehyphenate.
        remove_hyphen_list = []

        for text in lines:
            words = text.split()
            if len(words) == 0:
                continue
            for i in range(len(words)):
                # Remove any surrounding tags.
                stripped_word = self.strip_text(words[i].lower())
                if "-" in stripped_word:
                    if not stripped_word in hlist:
                        hlist.append(stripped_word)
                elif not stripped_word in wlist:
                    wlist.append(stripped_word)

        # Next, see if the dehypenated word is in the word list or the
        # common-word dictionary.
        for hw in hlist:
            if hw[0].isnumeric():
                continue
            term = hw.replace("-", "")
            if term in wlist:
                remove_hyphen_list.append(hw)
            elif term in self.dictionary:
                remove_hyphen_list.append(hw)
            elif self.simple_singular(term) in self.dictionary:
                remove_hyphen_list.append(hw)
            elif self.simple_present(term) in self.dictionary:
                remove_hyphen_list.append(hw)

        __logger__.debug(
            "word list for dehyphenation",
            extra={
                "props": {
                    "transformer": self.type,
                    "debug": str(remove_hyphen_list),
                }
            },
        )

        for text in lines:
            # Ignore blank lines.
            if len(text) == 0:
                content += "{}\n".format("")
                continue

            # Ignore table lines.
            if text[0] == "|":
                content += "{}\n".format(text)
                continue

            # Remove NL after a hyphen.
            words = text.split(" ")

            # Are we checking for a hyphenated word?
            for j in range(len(words)):
                stripped_word = self.strip_text(words[j].lower())
                if stripped_word in remove_hyphen_list:
                    words[j] = words[j].replace("-", "")
            content += "{}\n".format(" ".join(words))

        return content

    def transform(self, document: documents.Text) -> documents.Text:
        super().transform(document=document)

        # Read the common word dictionary
        if not os.path.exists(EN_DICTIONARY_PATH):
            __logger__.warning(
                "dictionary for dehyphenation",
                extra={
                    "props": {
                        "transformer": self.type,
                        "warning": str(EN_DICTIONARY_PATH + " not found"),
                    }
                },
            )
            nltk.download("words")
        for word in words.words():
            # Short words are not likely to be hyphenated, so...
            if len(word) > 5:
                self.dictionary.append(word)

        content = self.dehyphenate(document.content)

        return document.new_from(document, content=content)
