Example: Spreadsheets
=====================

In this example, we walk through a simple example of ingestion from an
CSV (comma separated values) spreadsheet source using the Ingestum Python
libraries.

Notes:

* Sorcero can also ingest XLS (Microsoft Excel) spreadsheets.

* You'll need to follow the the :doc:`installation` if you haven't used this library before.

* To learn more about the available ingestion sources, see :doc:`sources`.

See :ref:`Pipeline Example: Spreadsheets` below for a discussion of the pipeline
version of this same example.

----

Spreadsheets are some of the most common and flexible content types available,
and Sorcero provides a wide variety of tools with which spreadsheets can be
manipulated.

The source we use in the example is shown below::

    Username,Identifier,First name,Last name
    booker12,9012,Rachel,Booker
    grey07,2070,Laura,Grey
    johnson81,4081,Craig,Johnson
    jenkins46,9346,Mary,Jenkins
    smith79,5079,Jamie,Smith

Step 1: Import
--------------

Import three libraries from ingestum: ``documents``, ``sources``, and
``transformers``.

.. code-block:: python

    from ingestum import documents
    from ingestum import sources
    from ingestum import transformers

Step 2: Create an CSV source
----------------------------

Create an CSV source object from an CSV file.

.. code-block:: python

    csv_source = sources.CSV(path="tests/data/test.csv")


Step 3: Create a tabular document
---------------------------------

The next step is to convert our CSV document into a tabular
document. This is a unified document schema that all of the Sorcero
tabular transformers require.  We can use the
``CSVDocumentCreateTabular`` transformer to do this.

.. code-block:: python

    csv_document = transformers.CSVDocumentCreateTabular(
        document=csv_source
    )

The output of Step 3 is:

.. code-block:: json

    {
        "columns": 4,
        "content": [
            [
                "Username",
                "Identifier",
                "First name",
                "Last name"
            ],
            [
                "booker12",
                "9012",
                "Rachel",
                "Booker"
            ],
            [
                "grey07",
                "2070",
                "Laura",
                "Grey"
            ],
            [
                "johnson81",
                "4081",
                "Craig",
                "Johnson"
            ],
            [
                "jenkins46",
                "9346",
                "Mary",
                "Jenkins"
            ],
            [
                "smith79",
                "5079",
                "Jamie",
                "Smith"
            ]
        ],
        "pdf_context": null,
        "rows": 6,
        "title": "",
        "type": "tabular",
        "version": "1.0"
    }

If you have an XLS source, the process is very similar. Your source is
``sources.XLS``. You must specify the sheet you want to work with and
use the ``XLSSourceCreateCSVDocument`` transformer to extract that
sheet into a CSV document. From there, you can use the same
transformers as you would with CSV.

.. code-block:: python

    xls_source = sources.XLS(path="tests/data/test.xls")
    csv_document = transformers.XLSSourceCreateCSVDocument(
        sheet="Sheet1").transform(source=xls_source)

Step 4: Customize your tables
-----------------------------

Now's the fun part – customization. There are a number of options that
you can try to work with your table data but we'll only use one as an
example in this tutorial. ``TabularDocumentColumnInsert`` transforms a
Tabular document into another Tabular document where a new empty
column is inserted at the given position.

.. code-block:: python

    document = transformers.TabularDocumentColumnInsert(
        position=2,
        columns=1
    ).transform(document=csv_document)

The output of Step 4 is a table with a new column added:

.. code-block:: json

    {
        "columns": 5,
        "content": [
            [
                "Username",
                "Identifier",
                "",
                "First name",
                "Last name"
            ],
            [
                "booker12",
                "9012",
                "",
                "Rachel",
                "Booker"
            ],
            [
                "grey07",
                "2070",
                "",
                "Laura",
                "Grey"
            ],
            [
                "johnson81",
                "4081",
                "",
                "Craig",
                "Johnson"
            ],
            [
                "jenkins46",
                "9346",
                "",
                "Mary",
                "Jenkins"
            ],
            [
                "smith79",
                "5079",
                "",
                "Jamie",
                "Smith"
            ]
        ],
        "pdf_context": null,
        "rows": 6,
        "title": "",
        "type": "tabular",
        "version": "1.0"
    }

Pipeline Example: Spreadsheets
==============================

A Python script can be used to configure a pipeline. See
:doc:`pipelines` for more details.

1. Build the framework
----------------------

Just like in :doc:`example-text`, we'll start by adding some Python so
we can run our pipeline.

Add the following to an empty Python file:

.. code-block:: python

    import json
    import argparse
    import tempfile

    from ingestum import engine
    from ingestum import manifests
    from ingestum import pipelines
    from ingestum import transformers
    from ingestum.utils import stringify_document


    def generate_pipeline():
        pipeline = pipelines.base.Pipeline(
            name='default',
            pipes=[
                pipelines.base.Pipe(
                    name='default',
                    sources=[],
                    steps=[])])

        return pipeline


    def ingest(url):
        manifest = manifests.base.Manifest(
            sources=[])

        pipeline = generate_pipeline()
        workspace = tempfile.TemporaryDirectory()

        results, _ = engine.run(
            manifest=manifest,
            pipelines=[pipeline],
            pipelines_dir=None,
            artifacts_dir=None,
            workspace_dir=workspace.name)

        return results[0]


    def main():
        parser = argparse.ArgumentParser()
        subparser = parser.add_subparsers(dest='command', required=True)
        subparser.add_parser('export')
        ingest_parser = subparser.add_parser('ingest')
        ingest_parser.add_argument('url')
        args = parser.parse_args()

        if args.command == 'export':
            output = generate_pipeline()
        else:
            output = ingest(args.url)

        print(stringify_document(output))


    if __name__ == "__main__":
        main()

2. Import the source document
-----------------------------

In this pipeline, we'll be using an CSV source, so we should use
``sources.CSV(path)`` to define it. Next, convert it to a Sorcero CSV document
with the ``CSVSourceCreateDocument`` transformer. At the "Your pipeline goes
here" section of the template, add the following:

.. code-block:: python

    def generate_pipeline():
        pipeline = pipelines.base.Pipeline(
            name='default',
            pipes=[
                pipelines.base.Pipe(
                    name='default',
                    sources=[
                        pipelines.sources.Manifest(
                            source='csv')],

.. code-block:: python

    def ingest(url, target):
        manifest = manifests.base.Manifest(
            sources=[
                manifests.sources.CSV(
                    id='id',
                    pipeline='default',
                    url=url)])

3. Apply the transformers
-------------------------

At this point we can apply the same transformers we used in the
example above.

.. code-block:: python

    steps=[
        transformers.XLSSourceCreateCSVDocument(),
        transformers.CSVDocumentCreateTabular(),
        transformers.TabularDocumentColumnInsert(
            position=2,
            columns=1)]

4. Test your pipeline
---------------------

We're done! All we have to do is test it::

    $ python3 path/to/script.py ingest file://tests/data/test.csv

This tutorial gave some examples of what you can do with a CSV source, but it's
certainly not exhaustive. Sorcero provides a variety of tools to deal with
tabular documents – if you'd like to try them out, you can use them in step 4.
Check out our :doc:`reference` or our other :doc:`examples` for more ideas.

5. Export your pipeline
------------------------

    Python for humans, json for computers::

    $ python3 path/to/script.py export
