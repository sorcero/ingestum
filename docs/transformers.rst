Transformers Reference
======================

This is the reference page for transformers implementation and format.

Transformer Base Class
----------------------

.. automodule:: ingestum.transformers.base
   :exclude-members: Config

AudioSourceCreateTextDocument
-----------------------------

.. automodule:: ingestum.transformers.audio_source_create_text_document
   :exclude-members: extract

CollectionDocumentAdd
---------------------

.. automodule:: ingestum.transformers.collection_document_add

CollectionDocumentJoin
----------------------

.. automodule:: ingestum.transformers.collection_document_join

CollectionDocumentMerge
-----------------------

.. automodule:: ingestum.transformers.collection_document_merge

CollectionDocumentRemoveOnConditional
-------------------------------------

.. automodule:: ingestum.transformers.collection_document_remove_on_conditional

CollectionDocumentTransform
---------------------------

.. automodule:: ingestum.transformers.collection_document_transform

CollectionDocumentTransformOnConditional
----------------------------------------

.. automodule:: ingestum.transformers.collection_document_transform_on_conditional

CSVDocumentCreateTabular
------------------------

.. automodule:: ingestum.transformers.csv_document_create_tabular

CSVSourceCreateDocument
-----------------------

.. automodule:: ingestum.transformers.csv_source_create_document
   :exclude-members: extract_text

DocumentExtract
---------------

.. automodule:: ingestum.transformers.document_extract
   :exclude-members: preprocess_images, preprocess_document, extract

DocumentSourceCreateDocument
----------------------------

.. automodule:: ingestum.transformers.document_source_create_document

DOCXSourceCreateImage
----------------------------

.. automodule:: ingestum.transformers.docx_source_create_image
   :exclude-members: convert

DOCXSourceCreateTextDocument
----------------------------

.. automodule:: ingestum.transformers.docx_source_create_text_document
   :exclude-members: iter_picture_items, iter_block_items,
      extract_tabular_document, extract_resource_document, extract_table,
      extract_image, extract

EmailSourceCreateHTMLCollectionDocument
---------------------------------------

.. automodule:: ingestum.transformers.email_source_create_html_collection_document
   :exclude-members: extract

EmailSourceCreateTextCollectionDocument
---------------------------------------

.. automodule:: ingestum.transformers.email_source_create_text_collection_document
   :exclude-members: contentize, extract

FormDocumentSet
---------------

.. automodule:: ingestum.transformers.form_document_set

HTMLDocumentImagesExtract
-------------------------

.. automodule:: ingestum.transformers.html_document_images_extract
   :exclude-members: fetch, replace

HTMLDocumentSubReplaceForUnicode
--------------------------------

.. autoclass:: ingestum.transformers.html_document_sub_replace_for_unicode.Transformer
   :exclude-members: replace

HTMLDocumentSupReplaceForUnicode
--------------------------------

.. autoclass:: ingestum.transformers.html_document_sup_replace_for_unicode.Transformer
   :exclude-members: replace

HTMLSourceCreateDocument
------------------------

.. automodule:: ingestum.transformers.html_source_create_document
   :exclude-members: extract

HTMLSourceCreateImageSource
---------------------------

.. automodule:: ingestum.transformers.html_source_create_image_source
   :exclude-members: extract

ImageSourceCreateReferenceTextDocument
--------------------------------------

.. automodule:: ingestum.transformers.image_source_create_reference_text_document
   :exclude-members: extract

ImageSourceCreateTabularDocument
--------------------------------

.. automodule:: ingestum.transformers.image_source_create_tabular_document
   :exclude-members: text_from_rectangle, preprocess_for_text,
      preprocess_for_clusters, preprocess_for_lines, overlaps_vertically,
      overlaps_horizontally, overlaps, find_text_boxes, find_table_in_boxes,
      find_table_in_rectangle, build_lines, debug, extract

ImageSourceCreateTextDocument
-----------------------------

.. automodule:: ingestum.transformers.image_source_create_text_document
   :exclude-members: extract_text

PassageDocumentAddMetadataFromMetadata
--------------------------------------

.. automodule:: ingestum.transformers.passage_document_add_metadata_from_metadata
   :exclude-members: extract

PassageDocumentAddMetadata
--------------------------

.. automodule:: ingestum.transformers.passage_document_add_metadata
   :exclude-members: append_metadata

PassageDocumentAddMetadataOnAttribute
-------------------------------------

.. automodule:: ingestum.transformers.passage_document_add_metadata_on_attribute
   :exclude-members: metadata_with_metadata, extract

PassageDocumentStringSplit
--------------------------

.. automodule:: ingestum.transformers.passage_document_string_split
   :exclude-members: string_split

PassageDocumentTransformOnConditional
-------------------------------------

.. automodule:: ingestum.transformers.passage_document_transform_on_conditional

PDFSourceCreateFormDocument
---------------------------

.. automodule:: ingestum.transformers.pdf_source_create_form_document
   :exclude-members: extract

PDFSourceCreateTabularCollectionDocument
----------------------------------------

.. automodule:: ingestum.transformers.pdf_source_create_tabular_collection_document

PDFSourceCreateTextDocument
---------------------------

.. automodule:: ingestum.transformers.pdf_source_create_text_document
   :exclude-members: sort, sort_columns, similarity, find_neighbour, overlaps,
      find_column, find_columns, detect_layout, columnize, enrich, filter,
      collect, extract

PDFSourceCreateTextDocumentOCR
------------------------------

.. automodule:: ingestum.transformers.pdf_source_create_text_document_ocr

PDFSourceCreateTextDocumentReplacedExtractables
-----------------------------------------------

.. automodule:: ingestum.transformers.pdf_source_create_text_document_replaced_extractables
   :exclude-members: extract

PDFSourceCropCreateImageSource
------------------------------

.. automodule:: ingestum.transformers.pdf_source_crop_create_image_source

PDFSourceCropExtract
--------------------

.. automodule:: ingestum.transformers.pdf_source_crop_extract
   :extract-members: crop

PDFSourceImagesCreateResourceCollectionDocument
-----------------------------------------------

.. automodule:: ingestum.transformers.pdf_source_images_create_resource_collection_document

PDFSourceImagesExtract
----------------------

.. automodule:: ingestum.transformers.pdf_source_images_extract
   :exclude-members: extract, collect, dump

PDFSourceShapesCreateResourceCollectionDocument
-----------------------------------------------

.. automodule:: ingestum.transformers.pdf_source_shapes_create_resource_collection_document

PDFSourceShapesExtract
----------------------

.. automodule:: ingestum.transformers.pdf_source_shapes_extract
   :exclude-members: collect, process, dump, extract

PDFSourceTablesExtract
----------------------

.. automodule:: ingestum.transformers.pdf_source_tables_extract
   :exclude-members: export, get_size, discretize, extract

PDFSourceTextCreateTextCollectionDocument
-----------------------------------------

.. automodule:: ingestum.transformers.pdf_source_text_create_text_collection_document

PDFSourceTextExtract
--------------------

.. automodule:: ingestum.transformers.pdf_source_text_extract
   :exclude-members: dump, collect, extract

ProquestSourceCreateXMLCollectionDocument
-----------------------------------------

.. automodule:: ingestum.transformers.proquest_source_create_xml_collection_document
   :exclude-members: extract

PubmedSourceCreateTextCollectionDocument
-----------------------------------------

.. autoclass:: ingestum.transformers.pubmed_source_create_text_collection_document.Transformer
   :exclude-members: get_start, get_term, get_params, get_pmid, is_valid,
      result_handler, extract

PubmedSourceCreateXMLCollectionDocument
-----------------------------------------

.. autoclass:: ingestum.transformers.pubmed_source_create_xml_collection_document.Transformer
   :exclude-members: get_params, get_pmid, result_handler

RedditSourceCreateFormCollectionDocument
--------------------------

.. automodule:: ingestum.transformers.reddit_source_create_form_collection_document
   :exclude-members: search_reddit

ResourceCreateTextDocument
--------------------------

.. automodule:: ingestum.transformers.resource_create_text_document
   :exclude-members: extract

TabularDocumentCellTransposeOnConditional
-----------------------------------------

.. automodule:: ingestum.transformers.tabular_document_cell_transpose_on_conditional

TabularDocumentColumnsInsert
----------------------------

.. automodule:: ingestum.transformers.tabular_document_columns_insert

TabularDocumentColumnsStringReplace
-----------------------------------

.. automodule:: ingestum.transformers.tabular_document_columns_string_replace
   :exclude-members: replace

TabularDocumentColumnsUpdateWithExtractables
--------------------------------------------

.. automodule:: ingestum.transformers.tabular_document_columns_update_with_extractables
   :exclude-members: find_page, update_row, update_table

TabularDocumentCreateFormCollection
-----------------------------------

.. automodule:: ingestum.transformers.tabular_document_create_form_collection

TabularDocumentCreateFormCollectionWithHeaders
----------------------------------------------

.. automodule:: ingestum.transformers.tabular_document_create_form_collection_with_headers
   :exclude-members: convert

TabularDocumentCreateMDPassage
------------------------------

.. automodule:: ingestum.transformers.tabular_document_create_md_passage
   :exclude-members: convert

TabularDocumentFit
------------------

.. automodule:: ingestum.transformers.tabular_document_fit

TabularDocumentJoin
-------------------

.. automodule:: ingestum.transformers.tabular_document_join

TabularDocumentRowMergeOnConditional
------------------------------------

.. automodule:: ingestum.transformers.tabular_document_row_merge_on_conditional
   :exclude-members: merge

TabularDocumentRowRemoveOnConditional
-------------------------------------

.. automodule:: ingestum.transformers.tabular_document_row_remove_on_conditional

TabularDocumentStripUntilConditional
------------------------------------

.. automodule:: ingestum.transformers.tabular_document_strip_until_conditional

TextCreatePassageDocument
-------------------------

.. automodule:: ingestum.transformers.text_create_passage_document
   :exclude-members: extract_metadata

TextCreateXMLDocument
-------------------------

.. automodule:: ingestum.transformers.text_create_xml_document
   :exclude-members: extract_content

TextDocumentAddPassageMarker
----------------------------

.. automodule:: ingestum.transformers.text_document_add_passage_marker
   :exclude-members: add_markers

TextDocumentHyphensRemove
-------------------------

.. automodule:: ingestum.transformers.text_document_hyphens_remove
   :exclude-members: dehyphenate

TextDocumentJoin
----------------

.. automodule:: ingestum.transformers.text_document_join

TextDocumentStringReplace
-------------------------

.. automodule:: ingestum.transformers.text_document_string_replace
   :exclude-members: replace

TextSourceCreateDocument
------------------------

.. automodule:: ingestum.transformers.text_source_create_document
   :exclude-members: extract_text

TextSplitIntoCollectionDocument
--------------------------------

.. automodule:: ingestum.transformers.text_split_into_collection_document

TwitterSourceCreateFormCollectionDocument
-----------------------------------------

.. automodule:: ingestum.transformers.twitter_source_create_form_collection_document
   :exclude-members: search_twitter

XLSSourceCreateCSVCollectionDocument
------------------------------------

.. automodule:: ingestum.transformers.xls_source_create_csv_collection_document
   :exclude-members: extract_documents

XLSSourceCreateCSVDocument
--------------------------

.. automodule:: ingestum.transformers.xls_source_create_csv_document
   :exclude-members: extract_text

XLSSourceCreateImage
--------------------

.. automodule:: ingestum.transformer.xls_source_create_image
   :exclude-members: convert

XMLCreateTextDocument
---------------------

.. automodule:: ingestum.transformers.xml_create_text_document
   :exclude-members: tag_visible, extract

XMLDocumentTagReplace
---------------------

.. automodule:: ingestum.transformers.xml_document_tag_replace
   :members:
   :undoc-members:
   :show-inheritance:

XMLSourceCreateDocument
-----------------------

.. automodule:: ingestum.transformers.xml_source_create_document
