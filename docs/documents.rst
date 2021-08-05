Documents Reference
===================

This is the reference page for documents implementation and format.

Document Base Class
-------------------

.. automodule:: ingestum.documents.base
   :exclude-members: type, title, content, new_from

Collection
----------

.. automodule:: ingestum.documents.collection
   :exclude-members: content

Form
----

.. automodule:: ingestum.documents.form
   :exclude-members: content

HTML
----

.. automodule:: ingestum.documents.html
   :exclude-members: content

Passage
-------

.. autoclass:: ingestum.documents.passage.Document
   :exclude-members: content, metadata, new_from

   .. autoclass:: ingestum.documents.passage.Metadata
      :exclude-members: anchors, sha256, tags, types

Resource
--------

.. autoclass:: ingestum.documents.resource.Document
   :exclude-members: content, pdf_context, new_from

   .. autoclass:: ingestum.documents.resource.PDFContext
      :exclude-members: left, top, right, bottom, page

Tabular
-------

.. automodule:: ingestum.documents.tabular
   :exclude-members: colums, row, content, pdf_context, new_from

Text
----

.. automodule:: ingestum.documents.text
   :exclude-members: content, pdf_context, new_from

XML
---

.. automodule:: ingestum.documents.xml
   :exclude-members: content
