# Changelog

## [2.4.0] 2022-06-27

- Added figures and tables data in PubMed's full text.
- Added ingestum-install-plugins to manage dependencies without re-installing Ingestum.
- Fixed breaking EuropePMC ingestion on individual articles errors.
- Changed EuropePMC to a bigger PageSize for pagination.

## [2.3.0] 2022-06-13

- Fixed publication_date for PubMed based on PubModel data.
- Fixed removal of puntuations from PubMed full-text data.
- Fixed journal data for preprints in EuropePMC.
- Fixed regression with abstracts recursive tags in EuropePMC.
- Added ingestum-envelope to process full ingestion envelopes.

## [2.2.2] 2022-05-31

- Fixed default value for lists arguments in ingestum-generate-manifest.
- Fixed handling of missing objects in DOCX transformer.

## [2.2.1] 2022-05-21

- Fixed EuropePMC infinite loop condition.

## [2.2.0] 2022-05-19

- Added support for abstract_title search, sort and direction for bioRxiv.
- Added support for excluding sensitive arguments from documents context.
- Fixed EuropePMC abstract formatting.
- Fixed EuropePMC title formatting.
- Fixed EuropePMC publication_type formatting.
- Fixed leaking queries and search terms to documents context.
- Fixed leaking queries and search terms to debug logs.

## [2.1.0] - 2022-05-04

- Added support for PPTX as a source.
- Added memory instrumentation to ingestum-manifest.
- Fixed concepts, examples and typos in our documentation.
- Fixed scripts default arguments values to match sources default values.
- Fixed consistency of beautifulsoup's find_all method usage.
- Fixed ingestum-pipeline default argument value for lists.

## [2.0.3] - 2022-04-18

- Fixed PubMed abstracts to remove alternative language versions.

## [2.0.2] - 2022-04-11

- Fixed click version to 7.1.2.
- Changed black version back to 20.8b1.
- Changed typing-extensions version back to 3.7.4.3.
- Changed requests version to 2.25.1.

## [2.0.1] - 2022-04-07

- Added journal abbreviation to the publication document type.
- Fixed bioRxiv missing publication date.
- Fixed bioRxiv missing publication type.
- Fixed bioRxiv breaking on malformed data.
- Fixed bioRxiv abstract subtitles formatting.
- Fixed PDF page-number parsing logic.
- Fixed LitCovid tests.
- Changed black version to 22.3.0.
- Changed typing-extensions version to 3.10.0.2.

## [2.0.0] - 2021-12-16

- Added support for multiple source locations.
- Added support for multiple artifacts destinations.
- Added support for Google data lake.
- Added support for publications as a document type.
- Added support for LitCovid as a source.
- Added support for bioRxiv as a source.
- Added support for medRxiv as a source.
- Added support for EuropePMC as a source.
- Added support for multiple plugins directories.
- Added support for multithreaded processing.
- Added table extraction transformers based on text markers.
- Added hybrid PDF ingestion.
- Added hybrid PDF tables extraction.
- Added dynamic argument parsing to ingestum-pipeline tool.
- Added from_date and to_date arguments to all literature monitoring transformers.
- Added articles count parameter to Reddit transformer.
- Added ingestum-generate-manifest tool.
- Fixed CSV parsing issues.
- Fixed non-ASCII characters in output documents.
- Fixed sub-classing document types in plugins.
- Fixed PubMed transformers to handle missing hours attribute.
- Fixed ProQuest unicode issues.
- Fixed searching on documentation.
- Changed output documents to be unformatted to save storage space.
- Changed camelot-py version to 0.10.1.
- Changed praw version to 7.4.0.
- Changed Twitter back-end to tweepy.
- Changed pipeline names from 'excel' to 'xls'.
- Changed plugins folder structure to simplify plugin manager.
- Changed base operating system to Ubuntu 20.04 LTS.
- Removed CSV document type and related transformers.

## [1.3.0] - 2021-07-01

- Added a new "layout" argument to PDFSourceToTextDocument* transformers.
- Added Reddis source and transformer.
- Added "origin" attribute to all document types.
- Added support for recursive conditionals.
- Added tool to merge collection documents.
- Added support for Docker as a development environment.
- Added more details to the API documentation.
- Fixed transformers, documents and conditionals sub-classing.
- Fixed missing mimetype for .xlsx files.
- Fixed import attempts for unnecessary files in plugin directories.
- Fixed loading and deserializing manifest sources plugins.
- Fixed issue with pipeline messing with transformers when used multiple times.
- Changed logging format to JSON.
- Changed tests to pytest.
- Changed PubmedSourceCreate* transformer to use the official entrezpy library.
- Changed PubmedSourceCreate* "hours" argument to be optional.
- Changed PubmedSourceCreate* to use EDAT dates by default.
- Changed to distro-packaged LibreOffice installation.
- Changed artifacts IDs to be randomized.

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
