Example: XML Files
==================

In this example, we walk through a simple example of ingestion from an
XML source using the Ingestum Python libraries.

Notes:

* You'll need to follow the the :doc:`installation` if you haven't used this library before.

* To learn more about the available ingestion sources, see :doc:`sources`.

See :ref:`Pipeline Example: XML Files` below for a discussion of the
pipeline version of this same example.

----

The source we use in the example is shown below.

.. code-block:: XML

    <?xml version="1.0" encoding="UTF-8"?>
    <breakfast_menu>
    <food>
        <name>Belgian Waffles</name>
        ...
        <calories>950</calories>
    </food>
    </breakfast_menu>

Step 1: Import
--------------

Import three libraries from ingestum: ``documents``, ``sources``,
and ``transformers``.

.. code-block:: python

    from ingestum import documents
    from ingestum import sources
    from ingestum import transformers

Step 2: Create an XML source
----------------------------

Create an XML source object from an XML file.

.. code-block:: python

    xml_source = sources.XML(path="tests/data/test.xml")

Step 3: Create an XML document
------------------------------

Once we have the XML source object, we can apply transformers. The
first transformer we apply is ``XMLSourceCreateDocument``. This
transformer converts an XML source into an XML document.

.. code-block:: python

    document = transformers.XMLSourceCreateDocument().transform(
        source=xml_source
    )

As a result of Step 3, the content of the XML source document has been
embedded within a document structure within the object.

.. code-block:: json

    {
	"schema": "xml",
	"title": "",
	"content": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n
	<breakfast_menu>\n<food>\n    <name>Belgian Waffles</name>\n...
	<calories>950</calories>\n</food>\n</breakfast_menu>\n\n"
    }

Step 4: Create text document
----------------------------

Convert the XML to a text document by applying the
``XMLCreateTextDocument`` transformer. All of the XML tags will be
removed and the document type will be changed.

.. code-block:: python

    document = transformers.XMLCreateTextDocument().transform(
        document=document
    )

The output of Step 4 is shown below.

.. code-block:: json

    {
        "content": "\n\nBelgian Waffles\n...
        950\n\n",
        "title": "",
        "type": "text",
        "version": "1.0"
    }


Working with tags
-----------------

It is often useful to extract some meaning from select XML tags. For
example, we might want to create a separate document for each `food`
item in our breakfast menu.

We'll need to add an additional transformations between Steps 3 and
4 above.

Step 3.1: Add markers
---------------------

``XMLDocumentTagReplace`` can be used to modify the content
based on a tag. (Note that in XML, tags are case-sensitive, e.g.,
``<food>`` will not match ``<Food>`` or ``<FOOD>``.)

.. code-block:: python

    transformers.XMLDocumentTagReplace(
        tag='food',
        replacement='%s{@tag}' % "FOOD"
    )

In this example, we added a text marker, ``FOOD``, before each
``food`` tag in the document. We'll use this text in Step 5.

.. code-block:: json

    {
	"schema": "xml",
	"title": "",
	"content": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n
	<breakfast_menu>\nFOOD<food>\n    <name>Belgian Waffles</name>\n...
	<calories>950</calories>\n</food>\n</breakfast_menu>\n\n"
    }

Step 4: Create a text document
------------------------------

Convert the XML to a text document by applying the
``XMLCreateTextDocument`` transformer. All of the XML tags will be
removed and the document type will be changed.

.. code-block:: python

    document = transformers.XMLCreateTextDocument().transform(
        document=document
    )

The new output of Step 4 is shown below.

.. code-block:: json

    {
        "content": "\n\nFOODBelgian Waffles\n...
        950\n\n",
        "title": "",
        "type": "text",
        "version": "1.0"
    }

Step 5: Create the collection
-----------------------------

The ``FOOD`` marker is used to split the document into a collection of
documents.

.. code-block:: python

    transformers.TextSplitIntoCollectionDocument(
        separator='FOOD'
    )

The collection of text documents is shown below.

.. code-block:: json

    {
        "content":
        [
            {
                "content": "\n\nBelgian Waffles\n...",
                "title": "",
                "type": "text",
                "version": "1.0"
            },
            {
	        "content": "...",
            },
            {
                "content": "...950\n\n",
                "title": "",
                "type": "text",
                "version": "1.0"
            }
        ],
        "title": "",
        "type": "collection",
        "version": "1.0"
    }

Pipeline Example: XML Files
===========================

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

        print(json.dumps(output.dict(), indent=4, sort_keys=True))


    if __name__ == "__main__":
        main()

2. Import the source document
-----------------------------

In this pipeline, we'll be using an XML source, so we should use
``sources.XML(path)`` to define it. Next, convert it to a Sorcero XML
document with the ``XMLSourceCreateDocument`` transformer. At the
"Your pipeline goes here" section of the template, add the following:

.. code-block:: python

    def generate_pipeline():
        pipeline = pipelines.base.Pipeline(
            name='default',
            pipes=[
                pipelines.base.Pipe(
                    name='default',
                    sources=[
                        pipelines.sources.Manifest(
                            source='xml')],
                    steps=[
                        transformers.XMLSourceCreateDocument()])])

.. code-block:: python

    def ingest(url):
        manifest = manifests.base.Manifest(
            sources=[
                manifests.sources.XML(
                    id='id',
                    pipeline='default',
                    url=url)])

3. Apply the transformers
-------------------------

At this point we can apply the same transformers we used in the
example above.

.. code-block:: python

    steps=[
        transformers.XMLSourceCreateDocument(),
        transformers.XMLDocumentTagReplace(
            tag='food',
            replacement='%s{@tag}' % 'FOOD'
        ),
        transformers.XMLCreateTextDocument(),
        transformers.TextSplitIntoCollectionDocument(
            separator='FOOD'
        )]


4. Test your pipeline
---------------------

We're done! All we have to do is test it::

    $ python3 path/to/script.py ingest file://tests/data/test.xml

This tutorial gave some examples of what you can do with an XML
source, but it's certainly not exhaustive. Sorcero provides a variety
of tools to deal with XML documents and tags as well as text documents
– if you'd like to try them out, check out our :doc:`reference` or our
other :doc:`examples` for more ideas.

5. Export your pipeline
-----------------------

    Python for humans, json for computers::

    $ python3 path/to/script.py export
