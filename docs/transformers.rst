Transformers Reference
======================

This is the reference page for transformers implementation and format.

Transformer Base Class
----------------------

.. autoclass:: ingestum.transformers.base.Transformer
   :exclude-members: Config, type

AudioSourceCreateTextDocument
-----------------------------

.. autoclass:: ingestum.transformers.audio_source_create_text_document.Transformer
   :exclude-members: extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

BiorxivSourceCreatePublicationCollectionDocument
------------------------------------------------

.. autoclass:: ingestum.transformers.biorxiv_source_create_publication_collection_document.Transformer
   :exclude-members: get_authors, get_date, get_keywords, get_references, get_publication, get_page, process_page, extract
      arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

CollectionDocumentAdd
---------------------

.. autoclass:: ingestum.transformers.collection_document_add.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

CollectionDocumentJoin
----------------------

.. autoclass:: ingestum.transformers.collection_document_join.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

CollectionDocumentMerge
-----------------------

.. autoclass:: ingestum.transformers.collection_document_merge.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

CollectionDocumentRemoveOnConditional
-------------------------------------

.. autoclass:: ingestum.transformers.collection_document_remove_on_conditional.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

CollectionDocumentTransform
---------------------------

.. autoclass:: ingestum.transformers.collection_document_transform.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

CollectionDocumentTransformOnConditional
----------------------------------------

.. autoclass:: ingestum.transformers.collection_document_transform_on_conditional.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

CSVSourceCreateTabularDocument
------------------------------

.. autoclass:: ingestum.transformers.csv_source_create_tabular_document.Transformer
   :exclude-members: extract_text, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

DocumentExtract
---------------

.. autoclass:: ingestum.transformers.document_extract.Transformer
   :exclude-members: preprocess_images, preprocess_document, extract, arguments, 
      inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

DocumentSourceCreateDocument
----------------------------

.. autoclass:: ingestum.transformers.document_source_create_document.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

DOCXSourceCreateImage
----------------------------

.. autoclass:: ingestum.transformers.docx_source_create_image.Transformer
   :exclude-members: convert, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

DOCXSourceCreateTextDocument
----------------------------

.. autoclass:: ingestum.transformers.docx_source_create_text_document.Transformer
   :exclude-members: iter_picture_items, iter_block_items,
      extract_tabular_document, extract_resource_document, extract_table,
      extract_image, extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

EmailSourceCreateHTMLCollectionDocument
---------------------------------------

.. autoclass:: ingestum.transformers.email_source_create_html_collection_document.Transformer
   :exclude-members: extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

EmailSourceCreateTextCollectionDocument
---------------------------------------

.. autoclass:: ingestum.transformers.email_source_create_text_collection_document.Transformer
   :exclude-members: contentize, extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

EuropePMCSourceCreatePublicationCollectionDocument
--------------------------------------------------

.. autoclass:: ingestum.transformers.europepmc_source_create_publication_collection_document.Transformer
   :exclude-members: get_start, get_authors, get_full_text_url, get_keywords, get_publication_type,
      get_provider_url, get_origin, get_documents, extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

FormDocumentSet
---------------

.. autoclass:: ingestum.transformers.form_document_set.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

HTMLDocumentImagesExtract
-------------------------

.. autoclass:: ingestum.transformers.html_document_images_extract.Transformer
   :exclude-members: fetch, replace, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

HTMLDocumentSubReplaceForUnicode
--------------------------------

.. autoclass:: ingestum.transformers.html_document_sub_replace_for_unicode.Transformer
   :exclude-members: replace, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

HTMLDocumentSupReplaceForUnicode
--------------------------------

.. autoclass:: ingestum.transformers.html_document_sup_replace_for_unicode.Transformer
   :exclude-members: replace, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

HTMLSourceCreateDocument
------------------------

.. autoclass:: ingestum.transformers.html_source_create_document.Transformer
   :exclude-members: extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

HTMLSourceCreateImageSource
---------------------------

.. autoclass:: ingestum.transformers.html_source_create_image_source.Transformer
   :exclude-members: extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

ImageSourceCreateReferenceTextDocument
--------------------------------------

.. autoclass:: ingestum.transformers.image_source_create_reference_text_document.Transformer
   :exclude-members: extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

ImageSourceCreateTabularDocument
--------------------------------

.. autoclass:: ingestum.transformers.image_source_create_tabular_document.Transformer
   :exclude-members: text_from_rectangle, preprocess_for_text,
      preprocess_for_clusters, preprocess_for_lines, overlaps_vertically,
      overlaps_horizontally, overlaps, find_text_boxes, find_table_in_boxes,
      find_table_in_rectangle, build_lines, debug, extract,
      arguments, inputs, outputs, InputsModel, OutputsModel,
      find_cell_boundaries, sort_cells, rectangularize, filter, ArgumentsModel, type

ImageSourceCreateTextDocument
-----------------------------

.. autoclass:: ingestum.transformers.image_source_create_text_document.Transformer
   :exclude-members: extract_text, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

LitCovidSourceCreatePublicationCollectionDocument
-------------------------------------------------

.. autoclass:: ingestum.transformers.litcovid_source_create_publication_collection_document.Transformer
   :exclude-members: get_page_body_html, extract_from_litcovid, get_document, extract,
      arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type, 

PassageDocumentAddMetadataFromMetadata
--------------------------------------

.. autoclass:: ingestum.transformers.passage_document_add_metadata_from_metadata.Transformer
   :exclude-members: extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PassageDocumentAddMetadata
--------------------------

.. autoclass:: ingestum.transformers.passage_document_add_metadata.Transformer
   :exclude-members: append_metadata, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PassageDocumentAddMetadataOnAttribute
-------------------------------------

.. autoclass:: ingestum.transformers.passage_document_add_metadata_on_attribute.Transformer
   :exclude-members: metadata_with_metadata, extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PassageDocumentStringSplit
--------------------------

.. autoclass:: ingestum.transformers.passage_document_string_split.Transformer
   :exclude-members: string_split, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PassageDocumentTransformOnConditional
-------------------------------------

.. autoclass:: ingestum.transformers.passage_document_transform_on_conditional.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceCreateFormDocument
---------------------------

.. autoclass:: ingestum.transformers.pdf_source_create_form_document.Transformer
   :exclude-members: extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceCreatePublicationDocument
----------------------------------

.. autoclass:: ingestum.transformers.pdf_source_create_publication_document.Transformer
   :exclude-members: _is_complete, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceCreateTabularCollectionDocument
----------------------------------------

.. autoclass:: ingestum.transformers.pdf_source_create_tabular_collection_document.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceCreateTabularCollectionDocumentHybrid
----------------------------------------------

.. autoclass:: ingestum.transformers.pdf_source_create_tabular_collection_document_hybrid.Transformer
   :exclude-members: export, get_size, find_tables, extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceCreateTabularCollectionDocumentWithDividers
----------------------------------------------------

.. autoclass:: ingestum.transformers.pdf_source_create_tabular_collection_document_with_dividers.Transformer
   :exclude-members: combine_lines, find_coords, find_tables, export, get_size,
      discretize, extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceCreateTabularCollectionDocumentWithRegexp
--------------------------------------------------

.. autoclass:: ingestum.transformers.pdf_source_create_tabular_collection_document_with_regexp.Transformer
   :exclude-members: find_coords, find_tables, export, get_size, discretize, extract,
      arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceCreateTextDocument
---------------------------

.. autoclass:: ingestum.transformers.pdf_source_create_text_document.Transformer
   :exclude-members: sort, sort_columns, similarity, find_neighbour, overlaps,
      find_column, find_columns, detect_layout, columnize, enrich, filter,
      collect, extract, arguments, inputs, outputs, InputsModel, OutputsModel, type, ArgumentsModel

PDFSourceCreateTextDocumentHybrid
---------------------------------

.. autoclass:: ingestum.transformers.pdf_source_create_text_document_hybrid.Transformer
   :exclude-members: find_boxes, sort, sort_columns, similarity, find_neighbour, overlaps,
      find_column, find_columns, detect_layout, columnize, enrich, sort_elements,
      extract_ocr, extract_pdf, merge_lists, merge, is_overlapping, debug, extract,
      arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceCreateTextDocumentHybridReplacedExtractables
-----------------------------------------------------

.. autoclass:: ingestum.transformers.pdf_source_create_text_document_hybrid_replaced_extractables.Transformer
   :exclude-members: extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceCreateTextDocumentOCR
------------------------------

.. autoclass:: ingestum.transformers.pdf_source_create_text_document_ocr.Transformer
   :exclude-members: get_size, make_lines, sort, sort_columns, similarity, find_neighbour, overlaps, find_column, find_columns, detect_layout, columnize, enrich, extract,
      arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceCreateTextDocumentReplacedExtractables
-----------------------------------------------

.. autoclass:: ingestum.transformers.pdf_source_create_text_document_replaced_extractables.Transformer
   :exclude-members: extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceCropCreateImageSource
------------------------------

.. autoclass:: ingestum.transformers.pdf_source_crop_create_image_source.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceCropExtract
--------------------

.. autoclass:: ingestum.transformers.pdf_source_crop_extract.Transformer
   :exclude-members: crop, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceImagesCreateResourceCollectionDocument
-----------------------------------------------

.. autoclass:: ingestum.transformers.pdf_source_images_create_resource_collection_document.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceImagesExtract
----------------------

.. autoclass:: ingestum.transformers.pdf_source_images_extract.Transformer
   :exclude-members: extract, collect, dump, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceShapesCreateResourceCollectionDocument
-----------------------------------------------

.. autoclass:: ingestum.transformers.pdf_source_shapes_create_resource_collection_document.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceShapesExtract
----------------------

.. autoclass:: ingestum.transformers.pdf_source_shapes_extract.Transformer
   :exclude-members: collect, process, dump, extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceTablesExtract
----------------------

.. autoclass:: ingestum.transformers.pdf_source_tables_extract.Transformer
   :exclude-members: export, get_size, discretize, extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceTextCreateTextCollectionDocument
-----------------------------------------

.. autoclass:: ingestum.transformers.pdf_source_text_create_text_collection_document.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PDFSourceTextExtract
--------------------

.. autoclass:: ingestum.transformers.pdf_source_text_extract.Transformer
   :exclude-members: dump, collect, extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

ProquestSourceCreatePublicationCollectionDocument
-------------------------------------------------

.. autoclass:: ingestum.transformers.proquest_source_create_publication_collection_document.Transformer
   :exclude-members: get_authors, get_keywords, get_document, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

ProquestSourceCreateXMLCollectionDocument
-----------------------------------------

.. autoclass:: ingestum.transformers.proquest_source_create_xml_collection_document.Transformer
   :exclude-members: extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PubmedSourceCreatePublicationCollectionDocument
-----------------------------------------------

.. autoclass:: ingestum.transformers.pubmed_source_create_publication_collection_document.Transformer
   :exclude-members: get_authors, get_abstract, get_date_string, get_document, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

PubmedSourceCreateTextCollectionDocument
-----------------------------------------

.. autoclass:: ingestum.transformers.pubmed_source_create_text_collection_document.Transformer
   :exclude-members: get_start, get_term, get_params, get_pmid, is_valid,
      result_handler, extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type,
      get_document

PubmedSourceCreateXMLCollectionDocument
-----------------------------------------

.. autoclass:: ingestum.transformers.pubmed_source_create_xml_collection_document.Transformer
   :exclude-members: get_params, get_pmid, result_handler, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type, get_document
RedditSourceCreateFormCollectionDocument
----------------------------------------

.. autoclass:: ingestum.transformers.reddit_source_create_form_collection_document.Transformer
   :exclude-members: search_reddit, get_document, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

RedditSourceCreatePublicationCollectionDocument
-----------------------------------------------

.. autoclass:: ingestum.transformers.reddit_source_create_publication_collection_document.Transformer
   :exclude-members: get_document, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type,
      get_publication_date, get_publication_type, get_author

ResourceCreateTextDocument
--------------------------

.. autoclass:: ingestum.transformers.resource_create_text_document.Transformer
   :exclude-members: extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TabularDocumentCellTransposeOnConditional
-----------------------------------------

.. autoclass:: ingestum.transformers.tabular_document_cell_transpose_on_conditional.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TabularDocumentColumnsInsert
----------------------------

.. autoclass:: ingestum.transformers.tabular_document_columns_insert.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TabularDocumentColumnsStringReplace
-----------------------------------

.. autoclass:: ingestum.transformers.tabular_document_columns_string_replace.Transformer
   :exclude-members: replace, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TabularDocumentColumnsUpdateWithExtractables
--------------------------------------------

.. autoclass:: ingestum.transformers.tabular_document_columns_update_with_extractables.Transformer
   :exclude-members: find_page, update_row, update_table, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TabularDocumentCreateFormCollection
-----------------------------------

.. autoclass:: ingestum.transformers.tabular_document_create_form_collection.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TabularDocumentCreateFormCollectionWithHeaders
----------------------------------------------

.. autoclass:: ingestum.transformers.tabular_document_create_form_collection_with_headers.Transformer
   :exclude-members: convert, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TabularDocumentCreateMDPassage
------------------------------

.. autoclass:: ingestum.transformers.tabular_document_create_md_passage.Transformer
   :exclude-members: convert, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TabularDocumentFit
------------------

.. autoclass:: ingestum.transformers.tabular_document_fit.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TabularDocumentJoin
-------------------

.. autoclass:: ingestum.transformers.tabular_document_join.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TabularDocumentRowMergeOnConditional
------------------------------------

.. autoclass:: ingestum.transformers.tabular_document_row_merge_on_conditional.Transformer
   :exclude-members: merge, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TabularDocumentRowRemoveOnConditional
-------------------------------------

.. autoclass:: ingestum.transformers.tabular_document_row_remove_on_conditional.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TabularDocumentStripUntilConditional
------------------------------------

.. autoclass:: ingestum.transformers.tabular_document_strip_until_conditional.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TextCreatePassageDocument
-------------------------

.. autoclass:: ingestum.transformers.text_create_passage_document.Transformer
   :exclude-members: extract_metadata, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TextCreateXMLDocument
-------------------------

.. autoclass:: ingestum.transformers.text_create_xml_document.Transformer
   :exclude-members: extract_content, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TextDocumentAddPassageMarker
----------------------------

.. autoclass:: ingestum.transformers.text_document_add_passage_marker.Transformer
   :exclude-members: add_markers, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TextDocumentHyphensRemove
-------------------------

.. autoclass:: ingestum.transformers.text_document_hyphens_remove.Transformer
   :exclude-members: dehyphenate, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TextDocumentJoin
----------------

.. autoclass:: ingestum.transformers.text_document_join.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TextDocumentStringReplace
-------------------------

.. autoclass:: ingestum.transformers.text_document_string_replace.Transformer
   :exclude-members: replace, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TextSourceCreateDocument
------------------------

.. autoclass:: ingestum.transformers.text_source_create_document.Transformer
   :exclude-members: extract_text, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TextSplitIntoCollectionDocument
--------------------------------

.. autoclass:: ingestum.transformers.text_split_into_collection_document.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TwitterSourceCreateFormCollectionDocument
-----------------------------------------

.. autoclass:: ingestum.transformers.twitter_source_create_form_collection_document.Transformer
   :exclude-members: search_twitter, get_document, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

TwitterSourceCreatePublicationCollectionDocument
------------------------------------------------

.. autoclass:: ingestum.transformers.twitter_source_create_publication_collection_document.Transformer
   :exclude-members: search_twitter, get_document, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type,
      get_publication_date, get_publication_type, get_author, get_country, get_keywords, get_content

XLSSourceCreateImage
--------------------

.. autoclass:: ingestum.transformers.xls_source_create_image.Transformer
   :exclude-members: convert, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

XLSSourceCreateTabularCollectionDocument
----------------------------------------

.. autoclass:: ingestum.transformers.xls_source_create_tabular_collection_document.Transformer
   :exclude-members: extract_documents, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

XLSSourceCreateTabularDocument
------------------------------

.. autoclass:: ingestum.transformers.xls_source_create_tabular_document.Transformer
   :exclude-members: extract_text, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

XMLCreateTextDocument
---------------------

.. autoclass:: ingestum.transformers.xml_create_text_document.Transformer
   :exclude-members: tag_visible, extract, arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type

XMLDocumentTagReplace
---------------------

.. autoclass:: ingestum.transformers.xml_document_tag_replace.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type, replace

XMLSourceCreateDocument
-----------------------

.. autoclass:: ingestum.transformers.xml_source_create_document.Transformer
   :exclude-members: arguments, inputs, outputs, InputsModel, OutputsModel, ArgumentsModel, type
