Example: Webpages
==================

In this example, we walk through a simple example of ingestion from an HTML
source using the Ingestum Python libraries.

**Notes:**

* You'll need to follow the the :doc:`installation` if you haven't used this library before.

* HTML support is a subset of XML support, see :doc:`example-xml`.

* To learn more about the available ingestion sources, see :doc:`sources`.

For our sample document, we're going to use one of the test data documents
found in the library. If you'd like to follow along, you can find it
`here <https://gitlab.com/sorcero/community/ingestum/-
/blob/master/tests/data/test.html>`_.

See :ref:`pipeline_example_webpages` below for a discussion of the pipeline
version of this same example.

----

The source we use in the example is shown below.

.. code-block:: HTML

    <meta property="og:title" content="test">
    <body>this is a test</body>

Step 1: Import
--------------

Import three libraries from ingestum: ``documents``, ``sources``, and
``transformers``.

.. code-block:: python

    from ingestum import documents
    from ingestum import sources
    from ingestum import transformers

Step 2: Create an HTML source
-----------------------------

Create an HTML source object from an HTML file.

.. code-block:: python

    html_source = sources.HTML(path="tests/data/test.html")

Step 3: Create an HTML document
-------------------------------

We first need to apply ``HTMLSourceCreateDocument``. This transformer converts
an HTML source into an HTML document.

.. code-block:: python

    document = transformers.HTMLSourceCreateDocument().transform(
        source=html_source
    )

Let's look at each part of this line. ``transformers`` is the imported library
containing all transformers. ``HTMLSourceCreateDocument`` is our transformer, which has
no arguments. We then call the ``.transform()`` method, which takes one
argument, the source document we defined in the previous step.

As a result of Step 3, the content of the ``HTML`` source document has been
embedded within a document structure within the object.

.. code-block:: json

    {
        "content": "<html><head><meta content=\"test\" property=\"og:title\"/>\n</head><body>this is a test</body>\n</html>",
        "context": {},
        "origin": null,
        "title": "test",
        "type": "html",
        "version": "1.0"
    }



Step 4: Extract the images
--------------------------

Once we have the HTML document object, we can apply transformers. A typical
transformer to apply at this stage is ``HTMLDocumentImagesExtract`` in order
extract images from the HTML. Images will be placed in the directory specified
by the ``directory`` argument to the transformer.

.. code-block:: python

    transformers.HTMLDocumentImagesExtract(
        directory='tests/output'
    ).transform(document)

Step 5: Create a Text document
------------------------------

In this step, we extract the text from the HTML file using the
``XMLCreateTextDocument`` transformer. (Since HTML is a subset of XML, we can
use XML transformers on HTML documents.)

.. code-block:: python

    document = transformers.XMLCreateTextDocument().transform(
        document=document
    )

A byproduct of applying this transformer is that all of the tags have been
stripped from the text.

.. code-block:: json

    {
        "content": "this is a test",
        "context": {},
        "origin": null,
        "pdf_context": null,
        "title": "test",
        "type": "text",
        "version": "1.0"
    }

.. _pipeline_example_webpages:

Pipeline Example: Webpages
==========================

A Python script can be used to configure a pipeline. See :doc:`pipelines` for
more details.

1. Build the framework
----------------------

Just like in :doc:`example-text`, we'll start by adding some Python so we can
run our pipeline.

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
                    steps=[])])

        return pipeline


    def ingest(path, target):
        destination = tempfile.TemporaryDirectory()

        manifest = manifests.base.Manifest(
            sources=[])

        pipeline = generate_pipeline()

        results, *_ = engine.run(
            manifest=manifest,
            pipelines=[pipeline],
            pipelines_dir=None,
            artifacts_dir=None,
            workspace_dir=None)

        destination.cleanup()

        return results[0]


    def main():
        parser = argparse.ArgumentParser()
        subparser = parser.add_subparsers(dest='command', required=True)
        subparser.add_parser('export')
        ingest_parser = subparser.add_parser('ingest')
        ingest_parser.add_argument('path')
        ingest_parser.add_argument('target')
        args = parser.parse_args()

        if args.command == 'export':
            output = generate_pipeline()
        else:
            output = ingest(args.path, args.target)

        print(stringify_document(output))


    if __name__ == "__main__":
        main()

2. Define the sources
---------------------

The manifest lists the sources that will be ingested. In this case we only have a CSV as source,
so we create a ``manifests.sources.HTML`` source and add it to the collection of sources contained 
in the manifest. We also specify the source's standard arguments ``id``, ``pipeline``, 
``location``, and  ``destination``, as well as the source-specific argument ``target``.

.. code-block:: python

    def ingest(path, target):
        manifest = manifests.base.Manifest(
            sources=[
                manifests.sources.HTML(
                    id='id',
                    pipeline='default',
                    target=target,
                    location=manifests.sources.locations.Local(
                        path=path
                    ),
                    destination=manifests.sources.destinations.Local(
                        directory=destination.name
                    )
                )
            ]
        )

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
                            source='html'
                        )
                    ],
                    steps=[
                        transformers.HTMLSourceCreateDocument(),
                        transformers.HTMLDocumentImagesExtract(
                            directory='tests/files'
                        ),
                        transformers.XMLCreateTextDocument()
                    ]
                )
            ]
        )
    return pipeline

In this example we have only one pipe, which accepts a HTML file as input (specified by
``pipelines.sources.Manifest(source='html')``). The pipe sequentially applies three transformers 
to this source: ``transformers.HTMLSourceCreateDocument``, ``transformers.HTMLDocumentImagesExtract``,
and ``transformers.XMLCreateTextDocument``.

4. Test our pipeline
---------------------

We're done! All we have to do is test it:

.. code-block:: bash

    $ python3 path/to/script.py ingest tests/data/test.html body

Note that this example pipeline has only one pipe, we can add as many as we want.

This tutorial gave some examples of what we can do with a HTML source, but
it's certainly not exhaustive. Sorcero provides a variety of tools to deal with
HTML and passage documents. Check out our :doc:`reference` or our other
:doc:`examples` for more ideas.

5. Export our pipeline
------------------------

Python for humans, json for computers:

.. code-block:: bash

    $ python3 path/to/script.py export
