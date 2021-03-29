# -*- coding: utf-8 -*-

#
# Copyright (c) 2020,2021 Sorcero, Inc.
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


import sys

from ingestum.plugins import manager

from . import base

from . import html_source_create_document
from . import html_source_create_image_source
from . import html_document_sub_replace_for_unicode
from . import html_document_sup_replace_for_unicode
from . import html_document_images_extract

from . import image_source_create_text_document
from . import image_source_create_reference_text_document
from . import image_source_create_tabular_document

from . import pdf_source_tables_extract
from . import pdf_source_images_extract
from . import pdf_source_shapes_extract
from . import pdf_source_crop_extract
from . import pdf_source_text_extract
from . import pdf_source_create_text_document
from . import pdf_source_create_text_document_ocr
from . import pdf_source_create_text_document_replaced_extractables
from . import pdf_source_create_form_document
from . import pdf_source_create_tabular_collection_document
from . import pdf_source_images_create_resource_collection_document
from . import pdf_source_shapes_create_resource_collection_document
from . import pdf_source_text_create_text_collection_document
from . import pdf_source_crop_create_image_source

from . import text_source_create_document
from . import text_document_hyphens_remove
from . import text_document_string_replace
from . import text_document_add_passage_marker
from . import text_document_join
from . import text_split_into_collection_document
from . import text_create_passage_document
from . import text_create_xml_document

from . import xml_source_create_document
from . import xml_create_text_document
from . import xml_document_tag_replace

from . import passage_document_add_metadata
from . import passage_document_add_metadata_on_attribute
from . import passage_document_string_split
from . import passage_document_add_metadata_from_metadata

from . import collection_document_add
from . import collection_document_merge
from . import collection_document_remove_on_conditional

from . import csv_source_create_document
from . import csv_document_create_tabular

from . import xls_source_create_image
from . import xls_source_create_csv_document
from . import xls_source_create_csv_collection_document

from . import tabular_document_join
from . import tabular_document_fit
from . import tabular_document_create_form_collection
from . import tabular_document_create_md_passage
from . import tabular_document_cell_transpose_on_conditional
from . import tabular_document_row_remove_on_conditional
from . import tabular_document_row_merge_on_conditional
from . import tabular_document_columns_insert
from . import tabular_document_columns_string_replace
from . import tabular_document_columns_update_with_extractables
from . import tabular_document_create_form_collection_with_headers
from . import tabular_document_strip_until_conditional

from . import resource_create_text_document

from . import document_extract

from . import audio_source_create_text_document

from . import twitter_source_create_form_collection_document

from . import document_source_create_document

from . import email_source_create_text_collection_document
from . import email_source_create_html_collection_document

from . import proquest_source_create_xml_collection_document

from . import docx_source_create_image
from . import docx_source_create_text_document

from . import form_document_set

from . import pubmed_source_create_xml_collection_document
from . import pubmed_source_create_text_collection_document

# Load plugins
manager.default.register(sys.modules[__name__], "transformers", base.BaseTransformer)

# XXX these transformers need to import ALL other transformers
from . import passage_document_transform_on_conditional  # noqa E402
from . import collection_document_join  # noqa E402
from . import collection_document_transform  # noqa E402
from . import collection_document_transform_on_conditional  # noqa E402

HTMLDocumentSubReplaceForUnicode = html_document_sub_replace_for_unicode.Transformer
HTMLDocumentSupReplaceForUnicode = html_document_sup_replace_for_unicode.Transformer
HTMLSourceCreateDocument = html_source_create_document.Transformer
HTMLSourceCreateImageSource = html_source_create_image_source.Transformer
HTMLDocumentImagesExtract = html_document_images_extract.Transformer

ImageSourceCreateTextDocument = image_source_create_text_document.Transformer
ImageSourceCreateTabularDocument = image_source_create_tabular_document.Transformer
ImageSourceCreateReferenceTextDocument = (
    image_source_create_reference_text_document.Transformer
)

PDFSourceTablesExtract = pdf_source_tables_extract.Transformer
PDFSourceImagesExtract = pdf_source_images_extract.Transformer
PDFSourceShapesExtract = pdf_source_shapes_extract.Transformer
PDFSourceCropExtract = pdf_source_crop_extract.Transformer
PDFSourceTextExtract = pdf_source_text_extract.Transformer
PDFSourceCreateTextDocument = pdf_source_create_text_document.Transformer
PDFSourceCreateTextDocumentOCR = pdf_source_create_text_document_ocr.Transformer
PDFSourceCreateTextDocumentReplacedExtractables = (
    pdf_source_create_text_document_replaced_extractables.Transformer
)
PDFSourceCreateFormDocument = pdf_source_create_form_document.Transformer
PDFSourceCreateTabularCollectionDocument = (
    pdf_source_create_tabular_collection_document.Transformer
)
PDFSourceImagesCreateResourceCollectionDocument = (
    pdf_source_images_create_resource_collection_document.Transformer
)
PDFSourceShapesCreateResourceCollectionDocument = (
    pdf_source_shapes_create_resource_collection_document.Transformer
)
PDFSourceTextCreateTextCollectionDocument = (
    pdf_source_text_create_text_collection_document.Transformer
)
PDFSourceCropCreateImageSource = pdf_source_crop_create_image_source.Transformer

TwitterSourceCreateFormCollectionDocument = (
    twitter_source_create_form_collection_document.Transformer
)

TextSourceCreateDocument = text_source_create_document.Transformer
TextDocumentHyphensRemove = text_document_hyphens_remove.Transformer
TextDocumentStringReplace = text_document_string_replace.Transformer
TextDocumentAddPassageMarker = text_document_add_passage_marker.Transformer
TextDocumentJoin = text_document_join.Transformer
TextCreatePassageDocument = text_create_passage_document.Transformer
TextCreateXMLDocument = text_create_xml_document.Transformer
TextSplitIntoCollectionDocument = text_split_into_collection_document.Transformer

XMLSourceCreateDocument = xml_source_create_document.Transformer
XMLCreateTextDocument = xml_create_text_document.Transformer
XMLDocumentTagReplace = xml_document_tag_replace.Transformer

PassageDocumentAddMetadata = passage_document_add_metadata.Transformer
PassageDocumentAddMetadataOnAttribute = (
    passage_document_add_metadata_on_attribute.Transformer
)
PassageDocumentStringSplit = passage_document_string_split.Transformer
PassageDocumentTransformOnConditional = (
    passage_document_transform_on_conditional.Transformer
)
PassageDocumentAddMetadataFromMetadata = (
    passage_document_add_metadata_from_metadata.Transformer
)

CollectionDocumentAdd = collection_document_add.Transformer
CollectionDocumentJoin = collection_document_join.Transformer
CollectionDocumentMerge = collection_document_merge.Transformer
CollectionDocumentTransform = collection_document_transform.Transformer
CollectionDocumentTransformOnConditional = (
    collection_document_transform_on_conditional.Transformer
)
CollectionDocumentRemoveOnConditional = (
    collection_document_remove_on_conditional.Transformer
)

CSVSourceCreateDocument = csv_source_create_document.Transformer
CSVDocumentCreateTabular = csv_document_create_tabular.Transformer

XLSSourceCreateImage = xls_source_create_image.Transformer
XLSSourceCreateCSVDocument = xls_source_create_csv_document.Transformer
XLSSourceCreateCSVCollectionDocument = (
    xls_source_create_csv_collection_document.Transformer
)

TabularDocumentJoin = tabular_document_join.Transformer
TabularDocumentFit = tabular_document_fit.Transformer
TabularDocumentCreateFormCollection = (
    tabular_document_create_form_collection.Transformer
)
TabularDocumentCreateMDPassage = tabular_document_create_md_passage.Transformer
TabularDocumentRowRemoveOnConditional = (
    tabular_document_row_remove_on_conditional.Transformer
)
TabularDocumentCellTransposeOnConditional = (
    tabular_document_cell_transpose_on_conditional.Transformer
)
TabularDocumentRowMergeOnConditional = (
    tabular_document_row_merge_on_conditional.Transformer
)
TabularDocumentColumnsInsert = tabular_document_columns_insert.Transformer
TabularDocumentColumnsStringReplace = (
    tabular_document_columns_string_replace.Transformer
)
TabularDocumentColumnsUpdateWithExtractables = (
    tabular_document_columns_update_with_extractables.Transformer
)
TabularDocumentCreateFormCollectionWithHeaders = (
    tabular_document_create_form_collection_with_headers.Transformer
)
TabularDocumentStripUntilConditional = (
    tabular_document_strip_until_conditional.Transformer
)

ResourceCreateTextDocument = resource_create_text_document.Transformer

DocumentExtract = document_extract.Transformer

AudioSourceCreateTextDocument = audio_source_create_text_document.Transformer

DocumentSourceCreateDocument = document_source_create_document.Transformer

EmailSourceCreateTextCollectionDocument = (
    email_source_create_text_collection_document.Transformer
)
EmailSourceCreateHTMLCollectionDocument = (
    email_source_create_html_collection_document.Transformer
)

ProQuestSourceCreateXMLCollectionDocument = (
    proquest_source_create_xml_collection_document.Transformer
)

DOCXSourceCreateImage = docx_source_create_image.Transformer
DOCXSourceCreateTextDocument = docx_source_create_text_document.Transformer

FormDocumentSet = form_document_set.Transformer

PubmedSourceCreateXMLCollectionDocument = (
    pubmed_source_create_xml_collection_document.Transformer
)
PubmedSourceCreateTextCollectionDocument = (
    pubmed_source_create_text_collection_document.Transformer
)
