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


import logging

from typing_extensions import Literal

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import PDFObjRef, resolve1

from .local import LocalSource

__logger__ = logging.getLogger("ingestum")

METADATA = {
    "Title": "title",
}


class Source(LocalSource):
    """
    Class to support `PDF` input sources.
    """

    type: Literal["pdf"] = "pdf"

    @staticmethod
    def decode(value):
        if isinstance(value, PDFObjRef):
            value = resolve1(value)

        if not isinstance(value, bytes):
            return value

        for code in [8, 16, 32]:
            try:
                return value.decode("utf-%d" % code)
            except UnicodeDecodeError as e:
                __logger__.debug(str(e), extra={"props": {"source": "pdf"}})
                continue

        return value.decode("utf-8", "ignore")

    def get_pages(self):
        """
        :return: Page count of the PDF file
        :rtype: int
        """

        file = open(self.path, "rb")
        parser = PDFParser(file)
        document = PDFDocument(parser)

        count = resolve1(document.catalog["Pages"])["Count"]

        file.close()
        return count

    def get_metadata(self):
        """
        :return: Dictionary with the metadata (`title`) associated to this PDF
            source
        :rtype: dict
        """

        if self._metadata is not None:
            return self._metadata

        self._metadata = {}

        file = open(self.path, "rb")
        parser = PDFParser(file)
        document = PDFDocument(parser)

        # not all PDF provide this info
        if not document.info:
            file.close()
            return self._metadata

        info = document.info[0]
        for key in info:
            value = self.decode(info.get(key))
            self._metadata[METADATA.get(key, key)] = value

        file.close()
        return self._metadata
