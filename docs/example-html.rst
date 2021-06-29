Example: Webpages
==================

In this example, we walk through a simple example of ingestion from an HTML
source using the Ingestum Python libraries.

Notes:

* You'll need to follow the the :doc:`installation` if you haven't used this library before.

* HTML support is a subset of XML support, see :doc:`example-xml`.

* To learn more about the available ingestion sources, see :doc:`sources`.

See :ref:`Pipeline Example: Webpages` below for a discussion of the pipeline
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

Step 3: Extract the images
--------------------------

Once we have the HTML source object, we can apply transformers. A typical
transformer to apply at this stage is ``HTMLDocumentImagesExtract`` in order
extract images from the HTML. Images will be places in the directory specified
by the ``directory`` argument to the transformer.

.. code-block:: python

    transformers.HTMLDocumentImagesExtract(
        directory='tests/files'
    ).transform(html_source)

Step 4: Create an HTML document
-------------------------------

We'll also want to apply ``HTMLSourceCreateDocument``. This transformer converts
an HTML source into an HTML document.

.. code-block:: python

    document = transformers.HTMLSourceCreateDocument().transform(
        source=html_source
    )

As a result of Step 3, the content of the HTML source document has been embedded
within a document structure within the object.

.. code-block:: json

    {
        "schema": "html",
        "title": "",
        "content": "<meta property='og:title' content='test'><body>this is a test</body>"
    }

Step 5: Create a text document
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
        "title": "",
        "type": "text",
        "version": "1.0"
    }

Pipeline Example: Webpages
==========================

A Python script can be used to configure a pipeline. See :doc:`pipelines` for
more details.

1. Build the framework
----------------------

Just like in :doc:`example-text`, we'll start by adding some Python so we can
run our pipeline.

Add the following to an empty Python file:

.. code-block:: python

    import json
    import argparse
    import tempfile

    from ingestum import engine
    from ingestum import manifests
    from ingestum import pipelines
    from ingestum import transformers


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
        ingest_parser.add_argument('target')
        args = parser.parse_args()

        if args.command == 'export':
            output = generate_pipeline()
        else:
            output = ingest(args.url, args.target)

        print(json.dumps(output.dict(), indent=4, sort_keys=True))


    if __name__ == "__main__":
        main()

2. Import the source document
-----------------------------

In this pipeline, we'll be using an HTML source, so we should use
``sources.HTML(path)`` to define it. Next, convert it to a Sorcero HTML document
with the ``HTMLSourceCreateDocument`` transformer. At the "Your pipeline goes
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
                            source='html')],
                    steps=[
                        transformers.HTMLSourceCreateDocument(
                            target='')])])

.. code-block:: python

    def ingest(url, target):
        manifest = manifests.base.Manifest(
            sources=[
                manifests.sources.HTML(
                    id='id',
                    pipeline='default',
                    url=url,
                    target=target)])

3. Apply the transformers
-------------------------

At this point we can apply the same transformers we used in the example above.

.. code-block:: python

    steps=[
        transformers.HTMLSourceCreateDocument(),
        transformers.HTMLDocumentImagesExtract(
            directory='tests/files'),
        transformers.XMLCreateTextDocument()]

4. Test your pipeline
---------------------

We're done! All we have to do is test it::

    $ python3 path/to/script.py ingest file://tests/data/test.html body

This tutorial gave some examples of what you can do with a HTML source, but
it's certainly not exhaustive. Sorcero provides a variety of tools to deal with
HTML and passage documents. Check out our :doc:`reference` or our other
:doc:`examples` for more ideas.

5. Export your pipeline
------------------------

    Python for humans, json for computers::

    $ python3 path/to/script.py export
