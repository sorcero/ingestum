Ingestion Examples
==================

Code example
------------

The following example takes an HTML file, applies an HTML specific
transformer, to finally generate a Text document:

.. code-block:: python

    from ingestum import sources
    from ingestum import transformers

    source = sources.Text(path="tests/data/test.txt")
    document = transformers.TextSourceCreateDocument().transform(source)
    document = transformers.TextSplitIntoCollectionDocument(separator="\n\n").transform(document)

    print(document)

More examples
-------------

You can find annotated ingestion examples here. If you're new, we'd recommend
starting with :doc:`example-text` to get a taste of how ingestion works at
`Sorcero`. Note that the tutorials are designed with the assumption that you
have a basic understanding of the core concepts of ingestion (sources,
documents, transformers, conditionals, pipelines and manifests). If you need a
refresher, check out :doc:`basics`.

.. toctree::
   :maxdepth: 1

   example-text
   example-csv
   example-html
   example-pdf
   example-xml
