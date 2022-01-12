Example: Spreadsheets
=====================

In this example, we walk through a simple example of ingestion from an
CSV (comma separated values) spreadsheet source using the Ingestum Python
libraries.

**Notes:**

* Sorcero can also ingest XLS (Microsoft Excel) spreadsheets.

* You'll need to follow the the :doc:`installation` if you haven't used this library before.

* To learn more about the available ingestion sources, see :doc:`sources`.

For our sample document, we're going to use one of the test data documents
found in the library. If you'd like to follow along, you can find it
`here <https://gitlab.com/sorcero/community/ingestum/-
/blob/master/tests/data/test.csv>`_.

See :ref:`pipeline_example_spreadsheets` below for a discussion of the pipeline
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

Step 2: Create a CSV source
----------------------------

Create an CSV source object from an CSV file.

.. code-block:: python

    csv_source = sources.CSV(path="tests/data/test.csv")


Step 3: Create a Tabular document
---------------------------------

The next step is to convert our CSV source into a tabular
document. We can use the
``CSVSourceCreateTabularDocument`` transformer to do this.

.. code-block:: python

    tabular_document = transformers.CSVSourceCreateTabularDocument().transform(
        source=csv_source
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

If we have an XLS source, the process is very similar. Our source is
``sources.XLS``. We must specify the sheet we want to work with and
use the ``XLSSourceCreateTabularDocument`` transformer to extract that
sheet into a tabular document.

.. code-block:: python

    xls_source = sources.XLS(path="tests/data/test.xlsx")
    tabular_document = transformers.XLSSourceCreateTabularDocument(
        sheet="Sheet1").transform(source=xls_source)

Step 4: Customize our tables
-----------------------------

Now's the fun part – customization. There are a number of options that
we can try to work with our table data but we'll only use one as an
example in this tutorial. ``TabularDocumentColumnsInsert`` transforms a
Tabular document into another Tabular document where a new empty
column is inserted at the given position.

.. code-block:: python

    document = transformers.TabularDocumentColumnsInsert(
        position=2,
        columns=1
    ).transform(document=tabular_document)

The output of Step 4 is a table with a new column added:

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
                "",
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

.. _pipeline_example_spreadsheets:

Pipeline Example: Spreadsheets
==============================

A Python script can be used to configure a pipeline. See
:doc:`pipelines` for more details.

1. Build the framework
----------------------

Just like in :doc:`example-text`, we'll start by adding some Python so
we can run our pipeline.

The following block of code is a template with the basic structure needed
to configure an Ingestum Pipeline. Both the pipeline and the manifest are
initially empty. Add this to an empty Python file.

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
                    steps=[]
                )
            ]
        )

        return pipeline


    def ingest(path):
        destination = tempfile.TemporaryDirectory()

        manifest = manifests.base.Manifest(
            sources=[]
        )

        pipeline = generate_pipeline()

        results, *_ = engine.run(
            manifest=manifest,
            pipelines=[pipeline],
            pipelines_dir=None,
            artifacts_dir=None,
            workspace_dir=None
        )

        destination.cleanup()

        return results[0]


    def main():
        parser = argparse.ArgumentParser()
        subparser = parser.add_subparsers(dest='command', required=True)
        subparser.add_parser('export')
        ingest_parser = subparser.add_parser('ingest')
        ingest_parser.add_argument('path')
        args = parser.parse_args()

        if args.command == 'export':
            output = generate_pipeline()
        else:
            output = ingest(args.path)

        print(stringify_document(output))


    if __name__ == "__main__":
        main()

2. Define the sources
---------------------

The manifest lists the sources that will be ingested. In this case we only have a CSV as source,
so we create a ``manifests.sources.CSV`` source and add it to the collection of sources contained 
in the manifest. We also specify the source's standard arguments ``id``, ``pipeline``, 
``location``, and  ``destination``. 

.. code-block:: python

    def ingest(path):
        manifest = manifests.base.Manifest(
            sources=[
                manifests.sources.CSV(
                    id='id',
                    pipeline='default',
                    location=manifests.sources.locations.Local(
                        path=path,
                    ),
                    destination=manifests.sources.destinations.Local(
                        directory=destination.name,
                    )
                )
            ]
        )

Note that if the source had source-specific arguments, we would also include them here. These 
source-specific arguments would be previously passed as parameters to the ``ingest`` function.

3. Apply the transformers
-------------------------

For each pipe, we must specify which source will be accepted as input, as well
as the sequence of transformers that will be applied to the input source.

Note that, unlike manifest sources, the order in which transformers are listed matters (i.e. they aren't commutative).

.. code-block:: python

    def generate_pipeline():
        pipeline = pipelines.base.Pipeline(
            name='default',
            pipes=[
                pipelines.base.Pipe(
                    name='default',
                    sources=[
                        pipelines.sources.Manifest(
                            source='csv'
                        )
                    ],
                    steps=[
                        transformers.CSVSourceCreateTabularDocument(),
                        transformers.TabularDocumentColumnsInsert(
                            position=2,
                            columns=1
                        )
                    ]
                )
            ]
        )
    return pipeline

In this example we have only one pipe, which accepts a CSV file as input (specified by
``pipelines.sources.Manifest(source='csv')``). The pipe sequentially applies two transformers 
to this source: ``transformers.CSVSourceCreateTabularDocument`` and 
``transformers.TabularDocumentColumnsInsert``.

4. Test our pipeline
--------------------

We're done! All we have to do is test it:

.. code-block:: bash

    $ python3 path/to/script.py ingest tests/data/test.csv

Note that this example pipeline has only one pipe, we can add as many as we want.

This tutorial gave some examples of what we can do with a CSV source, but it's
certainly not exhaustive. Sorcero provides a variety of tools to deal with
tabular documents – if you'd like to try them out, you can use them in step 4 –.
Check out our :doc:`reference` or our other :doc:`examples` for more ideas.

5. Export our pipeline
------------------------

Python for humans, json for computers:

.. code-block:: bash

    $ python3 path/to/script.py export
