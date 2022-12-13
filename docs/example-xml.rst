Example: XML Files
==================

In this example, we walk through a simple example of ingestion from an XML
source using the Ingestum Python libraries.

**Notes:**

* You'll need to follow the the :doc:`installation` if you haven't used this library before.

* To learn more about the available ingestion sources, see :doc:`sources`.

For our sample document, we're going to use one of the test data documents
found in the library. If you'd like to follow along, you can find it
`here <https://gitlab.com/sorcero/community/ingestum/-
/blob/master/tests/data/test.xml>`_.

See :ref:`pipeline_example_xml` below for a discussion of the pipeline
version of this same example.

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

Import three libraries from ingestum: ``documents``, ``sources``, and
``transformers``.

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

Once we have the XML source object, we can apply transformers. The first
transformer we apply is ``XMLSourceCreateDocument``. This transformer converts
an XML source into an XML document.

.. code-block:: python

    document = transformers.XMLSourceCreateDocument().transform(
        source=xml_source
    )

As a result of Step 3, the content of the XML source document has been
embedded within a document structure within the object.

.. code-block:: json

    {
        "content": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<breakfast_menu>\n<food>\n    <name>Belgian Waffles</name>\n    <price>$5.95</price>\n    <description>\n   Two of our famous Belgian Waffles with plenty of real maple syrup\n   </description>\n    <calories>&lt;650</calories>\n</food>\n<food>\n    <name>Strawberry Belgian Waffles</name>\n    <price>$7.95</price>\n    <description>\n    Light Belgian waffles covered with strawberries and whipped cream\n    </description>\n    <calories>&gt;900</calories>\n</food>\n<food>\n    <name>Berry-Berry Belgian Waffles</name>\n    <price>$8.95</price>\n    <description>\n    Belgian waffles covered with assorted fresh berries and whipped cream\n    </description>\n    <calories>900</calories>\n</food>\n<food>\n    <name>French Toast</name>\n    <price>$4.50</price>\n    <description>\n    Thick slices made from our homemade sourdough bread\n    </description>\n    <calories>600</calories>\n</food>\n<food>\n    <name>Homestyle Breakfast</name>\n    <price>$6.95</price>\n    <description>\n    Two eggs, bacon or sausage, toast, and our ever-popular hash browns\n    </description>\n    <calories>950</calories>\n</food>\n</breakfast_menu>\n",
        "context": {},
        "origin": null,
        "title": "",
        "type": "xml",
        "version": "1.0"
    }

Step 4: Create a Text document
------------------------------

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
        "content": "\n\nBelgian Waffles\n...",
        "context": {},
        "origin": null,
        "pdf_context": null,
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
    ).transform(document=document)

In this example, we added a text marker, ``FOOD``, before each
``food`` tag in the document. We'll use this text in Step 5.

.. code-block:: json

    {
        "content": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n
        <breakfast_menu>\nFOOD<food>\n    <name>Belgian Waffles</name>\n...
        <calories>950</calories>\n</food>\n</breakfast_menu>\n\n"
        "context": {},
        "origin": null,
        "title": "",
        "type": "xml",
        "version": "1.0"
    }

Step 4: Create a Text document
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
        "content": "\n\nFOODBelgian Waffles\n...",
        "context": {},
        "origin": null,
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
    ).transform(document=document)

The collection of text documents is shown below.

.. code-block:: json

    {
        "content":
        [
            {
                "content": "\n\nBelgian Waffles\n...",
                "context": {},
                "origin": null,
                "title": "",
                "type": "text",
                "version": "1.0"
            },
            {
                "content": "..."
            },
            {
                "content": "...950\n\n",
                "context": {},
                "origin": null,
                "title": "",
                "type": "text",
                "version": "1.0"
            }
        ],
        "title": "",
        "context": {},
        "origin": null,
        "type": "collection",
        "version": "1.0"
    }

.. _pipeline_example_xml:

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


    def ingest(path):
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

The manifest lists the sources that will be ingested. In this case we only have an XML file 
as source, so we create a ``manifests.sources.XML`` source and add it to the collection of sources 
contained  in the manifest. We also specify the source's standard arguments ``id``, ``pipeline``, 
``location``, and  ``destination``. 

.. code-block:: python

    def ingest(path):
        manifest = manifests.base.Manifest(
            sources=[
                manifests.sources.XML(
                    id='id',
                    pipeline='default',
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

At this point we can apply the same transformers we used in the
example above.

.. code-block:: python

    def generate_pipeline():
        pipeline = pipelines.base.Pipeline(
            name='default',
            pipes=[
                pipelines.base.Pipe(
                    name='default',
                    sources=[
                        pipelines.sources.Manifest(
                            source='xml'
                        )
                    ],
                    steps=[
                        transformers.XMLSourceCreateDocument(),
                        transformers.XMLDocumentTagReplace(
                            tag='food',
                            replacement='%s{@tag}' % 'FOOD'
                        ),
                        transformers.XMLCreateTextDocument(),
                        transformers.TextSplitIntoCollectionDocument(
                            separator='FOOD'
                        )
                    ]
                )
            ]
        )
    return pipeline

In this example we have only one pipe, which accepts an XML file as input (specified by
``pipelines.sources.Manifest(source='xml')``). The pipe sequentially applies four transformers 
to this source: ``transformers.XMLSourceCreateDocument``, ``transformers.XMLDocumentTagReplace``,
``transformers.XMLCreateTextDocument``, and ``transformers.TextSplitIntoCollectionDocument``.


4. Test our pipeline
---------------------

We're done! All we have to do is test it:

.. code-block:: bash

    $ python3 path/to/script.py ingest tests/data/test.xml

Note that this example pipeline has only one pipe, we can add as many as we want.

This tutorial gave some examples of what we can do with an XML
source, but it's certainly not exhaustive. Sorcero provides a variety
of tools to deal with XML documents and tags as well as text documents
– if you'd like to try them out, check out our :doc:`reference` or our
other :doc:`examples` for more ideas.

5. Export our pipeline
-----------------------

Python for humans, json for computers:

.. code-block:: bash

    $ python3 path/to/script.py export
