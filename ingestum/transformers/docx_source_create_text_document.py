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

from pydantic import BaseModel
from typing import Optional
from typing_extensions import Literal

from docx import Document as DOCX
from docx.document import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

from .. import documents
from .. import sources
from .base import BaseTransformer
from .tabular_document_create_md_passage import Transformer as MDTransformer
from .resource_create_text_document import Transformer as RTransformer
from ..utils import write_document_to_path

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a `DOCX` source into a `Text` document where the text document
    contains all human-readable text from the source.
    """

    class ArgumentsModel(BaseModel):
        directory: str
        # TODO add table-to-text transformer
        # TODO add image-to-text transformer

    class InputsModel(BaseModel):
        source: sources.DOCX

    class OutputsModel(BaseModel):
        document: documents.Text

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    @staticmethod
    def iter_picture_items(parent):
        """
        Find all the pictures contained deep in this paragraph
        """
        for picture in parent.xpath(".//a:graphicData"):
            if picture.pic is None:
                continue
            yield picture.pic.blipFill.blip.embed

    @staticmethod
    def iter_block_items(parent):
        """
        Yield each paragraph and table child within *parent*, in document order.
        Each returned value is an instance of either Table or Paragraph. *parent*
        would most commonly be a reference to a main Document object, but
        also works for a _Cell object, which itself can contain paragraphs and tables.

        https://github.com/python-openxml/python-docx/issues/40
        """

        if isinstance(parent, Document):
            parent_elm = parent.element.body
        elif isinstance(parent, _Cell):
            parent_elm = parent._tc
        else:
            raise ValueError("something's not right")

        for child in parent_elm.iterchildren():
            if isinstance(child, CT_P):
                yield Paragraph(child, parent)
                for picture in Transformer.iter_picture_items(child):
                    yield picture
            elif isinstance(child, CT_Tbl):
                yield Table(child, parent)

    @staticmethod
    def extract_tabular_document(table):
        _table = []

        for row in table.rows:
            _row = []
            for cell in row.cells:
                _row.append(cell.text)
            _table.append(_row)

        rows = len(_table)
        columns = len(_table[0]) if rows else 0

        return documents.Tabular.new_from(
            None, content=_table, rows=rows, columns=columns
        )

    @staticmethod
    def extract_resource_document(document, path, r_id):
        part = document.part.related_parts[r_id]

        with open(path, "wb") as _file:
            _file.write(part._blob)

        return documents.Resource.new_from(None, content=path)

    def extract_image(self, document, r_id):
        name = "image_%06d" % self._images_count
        path = os.path.join(self.arguments.directory, name)
        document = self.extract_resource_document(document, path, r_id)
        return RTransformer.extract(document.content)

    def extract_table(self, table):
        document = self.extract_tabular_document(table)

        # dump it to the output directory
        name = "table_%06d.json" % self._tables_count
        path = os.path.join(self.arguments.directory, name)
        write_document_to_path(document, path)

        transformer = MDTransformer(format=None)
        return transformer.convert(document.content)

    def extract(self, source):
        self._tables_count = 0
        self._images_count = 0

        content = ""

        document = DOCX(source.path)
        for block in self.iter_block_items(document):
            if isinstance(block, Paragraph):
                content += f"{block.text}\n"
            elif isinstance(block, Table):
                content += f"{self.extract_table(block)}\n"
                self._tables_count += 1
            elif isinstance(block, str):
                content += f"{self.extract_image(document, block)}\n"
                self._images_count += 1

        return content

    def transform(self, source: sources.DOCX) -> sources.Text:
        super().transform(source=source)

        return documents.Text.new_from(source, content=self.extract(source))
