# -*- coding: utf-8 -*-

#
# Copyright (c) 2021 Sorcero, Inc.
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

from .. import sources
from .. import documents
from .base import BaseTransformer
from .pdf_source_create_text_document_hybrid import Layout
from .pdf_source_create_text_document_hybrid import CropArea
from .pdf_source_create_text_document_hybrid import Transformer as TTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a `PDF` input source into a `Text` document where the Text
    document contains all human-readable text from the PDF, using a combination
    of text extraction and OCR techniques.

    This variant can also handle transformations for extractables.

    :param first_page: First page to be used
    :type first_page: int
    :param last_page: Last page to be used
    :type last_page: int
    :param options: Dictionary with params for the underlying library
    :type options: dict
    :param tolerance: The margin of error, in pixels, of bounding box and text
        box coordinates when performing comparative PDF text ingestion.
    :type tolerance: int
    :param crop: Dictionary with left, top, right and bottom coordinates to be
        included from the page, expressed in percentages. E.g. ``top=0.1`` and
        ``bottom=0.9``, means everything that comes before that first ten
        percent and that last ten percent will be excluded. Note that the page
        is defined as the PDF MediaBox, which may be slightly larger than the
        viewable/printable CropBox displayed in PDF viewers.
    :type crop: CropArea
    :param layout:
        * ``single`` will re-order the text assuming a single column layout
        * ``multi`` will re-order the text assuming a multi column layout
        * ``auto`` will try to infer the text layout and re-order text accordingly
    :type layout: Layout
    :param reader: The PDF reader to use in order to find content areas,
        ``opencv`` (default) or ``adobe``.
    :type reader: str
    """

    class ArgumentsModel(BaseModel):
        first_page: Optional[int] = -1
        last_page: Optional[int] = -1
        options: Optional[dict] = None
        tolerance: Optional[int] = 10
        crop: Optional[CropArea] = CropArea(top=0, bottom=1, left=0, right=1)
        layout: Optional[Layout] = "auto"
        reader: Optional[str] = "opencv"

    class InputsModel(BaseModel):
        source: sources.PDF
        collection: documents.Collection
        replacements: Optional[documents.Collection]

    class OutputsModel(BaseModel):
        document: documents.Text

    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    type: Literal[__script__] = __script__

    def extract(self, source, collection, replacements):
        return TTransformer(
            first_page=(
                self.arguments.first_page if self.arguments.first_page > 0 else 1
            ),
            last_page=(
                self.arguments.last_page
                if self.arguments.last_page > 0
                else source.get_pages()
            ),
            options=self.arguments.options,
            tolerance=self.arguments.tolerance,
            crop=self.arguments.crop,
            layout=self.arguments.layout,
            reader=self.arguments.reader,
        ).extract(source, collection, replacements)

    def transform(
        self,
        source: sources.PDF,
        collection: documents.Collection,
        replacements: documents.Collection,
    ) -> documents.Text:
        super().transform(
            source=source, collection=collection, replacements=replacements
        )

        return documents.Text.new_from(
            source, content=self.extract(source, collection, replacements)
        )
