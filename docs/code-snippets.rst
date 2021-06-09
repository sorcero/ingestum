Code Snippets
=============

Below, you'll find short code snippets to do common ingestion
tasks. Please add your own snippets via a merge request.

Converting HTML links to Markdown
---------------------------------

When writing regular expressions with XML and HTML, you can refer to
tags with ``{@tag}`` and the text contained in a tag with
``{@text}``. Tag attributes are referred to with ``{attribute name}``.

To convert links in HTML into Markdown, the text inside the
``<a> </a>`` tags is placed inside []s, followed by the contents of the
``href`` attribute, which is placed inside ()s.

.. code-block:: python

    # Convert HTML links to Markdown format
    transformers.XMLDocumentTagReplace(
        tag='a',
        replacement=' [{@text}]({href}) '
    )

Converting an XML strong tag to Markdown
----------------------------------------

You can convert a strong tag to Markdown by placing a ``*`` on either
side of the tag. After the tags are removed (during conversion to a
text document), the Markdown will remain embedded in the text.

.. code-block:: python

    transformers.XMLDocumentTagReplace(
        tag='strong',
        replacement='*{@tag}*'
    )

Creating a collection from paragraph tags in HTML
-------------------------------------------------

One way to create a collection of paragraphs is to insert a marker
into the ``<p>`` tag.

.. code-block:: python

    transformers.XMLDocumentTagReplace(
        tag='p',
        replacement='PARAGRAPH_MARKER{@tag}'
    )

After converting the HTML to text, you can split the text at the
markers.

.. code-block:: python

    transformers.XMLCreateTextDocument(),
    transformers.TextSplitIntoCollectionDocument(
        separator='PARAGRAPH_MARKER'
    )

Create Markdown tables from Excel
---------------------------------

XLS is treated much like CSV, except that each sheet in the XLS file
is used to create a Document in a Collection of Documents. The tabular
format is a list of lists, where each row is a list of column
entries. TabularDocumentCreateMDPassage converts to Markdown.

.. code-block:: python

    transformers.XLSSourceCreateCSVCollectionDocument(),
    transformers.CollectionDocumentTransform(
        transformer=transformers.CSVDocumentCreateTabular()
    ),
    transformers.CollectionDocumentTransform(
        transformer=transformers.TabularDocumentCreateMDPassage()
    )

Merging sheets in a spreadsheet
-------------------------------

We treat XLS much like we treat CSV, except that we walk through each
sheet in the XLS file to create a collection of documents as opposed
to a single document.

.. code-block:: python

    transformers.XLSSourceCreateCSVCollectionDocument()

The tabular format is a list of lists, where each row is a list of
column entries; after applying the CSVDocumentCreateTabular
transformer, you have a collection of lists of lists (i.e., one list
of lists per sheet).

.. code-block:: python

    transformers.CollectionDocumentTransform(
        transformer=transformers.CSVDocumentCreateTabular()
    )

In some cases, it is desirable to merge all of the sheets into a
single list of lists.

.. code-block:: python

    transformers.CollectionDocumentJoin(
        transformer=transformers.TabularDocumentJoin(),
    )
