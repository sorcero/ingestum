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

from .. import sources
from .. import documents
from .base import BaseTransformer
from .pdf_source_create_text_document import Layout
from .pdf_source_create_text_document import CropArea
from .pdf_source_create_text_document import Transformer as TTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a `PDF` input source into a `Text` document where the Text
    document contains all human-readable text from the PDF.

    This variant can also handle transformations for extractables.

    :param first_page: First page to be used
    :type first_page: int
    :param last_page: Last page to be used
    :type last_page: int
    :param options: Dictionary with params for the underlying library
    :type options: dict
    :type crop: CropArea
        Dictionary with left, top, right and bottom coordinates
        to be included from the page, expressed in percentages.
        E.g. top=0.1 and bottom=0.9, means everything that comes
        before that first ten percent and that last ten percent
        will be excluded.
    :param layout:
        * ``original`` will preserve the original PDF text order,
        * ``single`` will re-order the text assuming a single column layout
        * ``multi`` will re-order the text assuming a multi column layout
        * ``auto`` will try to infer the text layout and re-order text accordingly
    :type layout: Layout
    """

    class ArgumentsModel(BaseModel):
        first_page: Optional[int] = None
        last_page: Optional[int] = None
        options: Optional[dict] = None
        crop: Optional[CropArea] = None
        layout: Optional[Layout] = "auto"

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
            first_page=self.arguments.first_page,
            last_page=self.arguments.last_page,
            options=self.arguments.options,
            crop=self.arguments.crop,
            layout=self.arguments.layout,
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
