# Changelog

## [1.2.1] - 2021-03-29

- Fixed extracting sources mimetypes.
- Fixed OR vs AND syntax in PubMed queries.
- Fixed deserializing pipelines with recursive transformers.

## [1.2.0] - 2021-03-19

- Added support for converting HTML to Image source.
- Added support for converting XLS to Image source.
- Added support for converting DOCX to Image source.
- Added support for unspecified number of pages in PDF transformers.
- Added support for recursive transformers, e.g. for collections of collections.
- Added support for context metadata in all document formats.
- Added support for types field in Passage document metadata.
- Added support for toolbox containers as development environment.
- Added ingestum-migrate for existing ingestum documents, e.g for testing outputs.
- Added debug logging calls to all transformers.
- Added debug logging calls to all time critical pipeline steps.
- Fixed opening the same PDF repeatedly for metadata.
- Fixed handling empty PDF pages.
- Fixed source downloading cache.
- Changed to a richer PubMed API.

## [1.1.0] - 2021-02-11

- Added support for DOCX sources.
- Added support for PubMed sources.
- Added support for crop area in PDF source transformer.
- Added support for table extraction from images.
- Added support for PDF unstructured forms.
- Added option to disable PDF columns layot detection.
- Added more examples to documentation.
- Added filters to XML source transformer to reduce noise in output text.
- Fixed PDF column extraction for more complex layouts.
- Fixed error on Text document tokenizer not handling empty lists.
- Fixed error message for non-existent files.
- Fixed errors while ingesting PDF with protections enabled.
- Fixed errors while ingesting PDF with watermarks.
- Fixed errors while ingesting PDF with noisy shape data.
- Fixed errors with HTML parser by switching to lxml.
- Fixed memory consumption in PDF OCR transformers.
- Updated documentation.
- Updated pyexcel requirement to v0.6.6.

## [1.0.2] - 2020-12-10

- Fixed paragraph detection for PDF and OCR pipelines.
- Fixed dealing with PDF images extraction with noisy data.

## [1.0.1] - 2020-11-30

- Changed version of requests to 2.24.0.

## [1.0.0] - 2020-11-30

- Initial release.
