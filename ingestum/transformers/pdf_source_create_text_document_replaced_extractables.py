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
from .pdf_source_create_text_document import CropArea
from .pdf_source_create_text_document import Transformer as TTransformer

__script__ = os.path.basename(__file__).replace(".py", "")


class Transformer(BaseTransformer):
    """
    Transforms a PDF input source into a Text document where
    the Text document contains all human-readable text from
    the PDF.

    This variant can also handle transformations for extractables.

    Parameters
    ----------
    first_page : int
        First page to be used
    last_page : int
        Last page to be used
    options: dict
        Dictionary with params for the underlying library
    crop: dict
        Dictionary with left, top, right and bottom coordinates
        to be included from the page, expressed in percentages.
        E.g. top=0.1 and bottom=0.9, means everything that comes
        before that first ten percent and that last ten percent
        will be excluded.
    layout_dectection: bool
        Whether it should try to reconstruct each page text
        layout as a human would read it.
    """

    class ArgumentsModel(BaseModel):
        first_page: Optional[int] = None
        last_page: Optional[int] = None
        options: Optional[dict] = None
        crop: Optional[CropArea] = None
        layout_detection: Optional[bool] = True

    class InputsModel(BaseModel):
        source: sources.PDF
        collection: documents.Collection
        replacements: Optional[documents.Collection]

    class OutputsModel(BaseModel):
        document: documents.Text

    type: Literal[__script__] = __script__
    arguments: ArgumentsModel
    inputs: Optional[InputsModel]
    outputs: Optional[OutputsModel]

    def extract(self, source, collection, replacements):
        return TTransformer(
            first_page=self.arguments.first_page,
            last_page=self.arguments.last_page,
            options=self.arguments.options,
            crop=self.arguments.crop,
            layout_detection=self.arguments.layout_detection,
        ).extract(source, collection, replacements)

    def transform(self, source, collection, replacements):
        super().transform(
            source=source, collection=collection, replacements=replacements
        )

        return documents.Text.new_from(
            source, content=self.extract(source, collection, replacements)
        )
