Documents Reference
===================

This is the reference page for documents implementation and format.

Document Base Class
-------------------

.. automodule:: ingestum.documents.base
   :exclude-members: type, title, content, new_from, type

Collection
----------

.. automodule:: ingestum.documents.collection
   :exclude-members: content, type

Form
----

.. automodule:: ingestum.documents.form
   :exclude-members: content, type

HTML
----

.. automodule:: ingestum.documents.html
   :exclude-members: content, type

Passage
-------

.. autoclass:: ingestum.documents.passage.Document
   :exclude-members: content, metadata, new_from, type

   .. autoclass:: ingestum.documents.passage.Metadata
      :exclude-members: anchors, sha256, tags, types

Publication
-----------

.. autoclass:: ingestum.documents.publication.Document
   :exclude-members: content, authors, new_from, abstract, keywords
      language, publication_date, journal, journal_ISSN, references,
      entrez_date, provider, provider_id, provider_url, country,
      publication_type, full_text_url, coi_statement, doi, type,
      keywords, language, copyright

   .. autoclass:: ingestum.documents.publication.Author
      :exclude-members: name, affiliation

Resource
--------

.. autoclass:: ingestum.documents.resource.Document
   :exclude-members: content, pdf_context, new_from, source, type

   .. autoclass:: ingestum.documents.resource.PDFContext
      :exclude-members: left, top, right, bottom, page

Tabular
-------

.. automodule:: ingestum.documents.tabular
   :exclude-members: columns, rows, content, pdf_context, new_from, type

Text
----

.. automodule:: ingestum.documents.text
   :exclude-members: content, pdf_context, new_from, type

XML
---

.. automodule:: ingestum.documents.xml
   :exclude-members: content, type
