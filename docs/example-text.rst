Example: Text Files
===================

The text source is one of the most straightforward source types to ingest, and
`Sorcero` provides several tools that we can use to make our ingestion process
easier and more useful. We're going to start with a sample text document and
perform a number of transformations that will convert it to a collection of
passage documents.

**Notes:**

* You'll need to follow the the :doc:`installation` if you haven't used this library before.

* To learn more about the available ingestion sources, see :doc:`sources`.

For our sample document, we're going to use one of the test data documents
found in the library. If you'd like to follow along, you can find it
`here <https://gitlab.com/sorcero/community/ingestum/-
/blob/master/tests/data/test.txt>`_.

See :ref:`pipeline_example_text` below for a discussion of the
pipeline version of this same example.

----

The source we use in the example is shown below:

.. code-block:: text

    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do ...
    vulputate eu scelerisque felis. Faucibus nisl tincidunt eget nullam.

    Fringilla phasellus faucibus scelerisque eleifend. Volutpat commodo...
    faucibus in ornare quam. Felis eget nunc lobortis mattis.

    Risus nec feugiat in fermentum posuere. Odio ut enim blandit volutpat...
    et egestas quis ip\n-sum suspendisse... congue mauris rhoncus aenean.

    Pulvinar mattis nunc sed blandit libero volutpat sed cras. Id porta...
    fringilla. Morbi enim nunc faucibus a.

    Sollicitudin nibh sit amet commodo nulla facilisi nullam...
    viverra orci sagittis eu.

Step 1: Import
--------------

Import three libraries from ``ingestum``: ``documents``, ``sources``,
and ``transformers``.

.. code-block:: python

    from ingestum import documents
    from ingestum import sources
    from ingestum import transformers

Step 2: Create a Text source
-----------------------------

In this example, we are using a text source, so we use ``sources.Text(path)`` to
define the source type. This retrives the source document at the path provided
and identifies it as a text source document.

.. code-block:: python

    text_source = sources.Text(path="tests/data/test.txt")

Step 3: Create a Text document
------------------------------

Once we have the Text source object, we can apply transformers. The first
transformer we apply is ``TextSourceCreateDocument``. This transformer converts
a Text source into a Text document.

.. code-block:: python

    document = transformers.TextSourceCreateDocument().transform(
        source=text_source
    )

Let's look at each part of this line. ``transformers`` is the imported library
containing all transformers. ``TextSourceCreateDocument`` is our transformer, which has
no arguments. We then call the ``.transform()`` method, which takes one
argument, the source document we defined in the previous step.

As a result of Step 3, the content of the ``Text`` source document has been
embedded within a document structure within the object.

.. code-block:: json

    {
        "content": "Lorem ipsum dolor sit amet, consectetur adipiscing
        elit, sed do... vulputate eu scelerisque felis. Faucibus nisl
        tincidunt eget nullam.\n\nFringilla phasellus faucibus scelerisque
        eleifend. Volutpat commodo... faucibus in ornare quam. Felis eget
        nunc lobortis mattis.\n\nRisus nec feugiat in fermentum
        posuere. Odio ut enim blandit volutpat... et egestas quis ip\n-sum
        suspendisse... congue mauris rhoncus aenean.\n\nPulvinar mattis
        nunc sed blandit libero volutpat sed cras. Id
        porta... fringilla. Morbi enim nunc faucibus a.\n\nSollicitudin
        nibh sit amet commodo nulla facilisi nullam... viverra orci
        sagittis eu.\n",
        "context": {},
        "origin": null,
        "pdf_context": null,
        "title": "",
        "type": "text",
        "version": "1.0"
    }

Step 4: Remove hyphenations
---------------------------

Now that we've got a text document, we can use a variety of tools that will
allow us to tune the content. For example, there are some hyphenated word, such
as "ip-\nsum". We can use ``TextDocumentHyphensRemove`` to remove the hyphens.

.. code-block:: python

    document = transformers.TextDocumentHyphensRemove().transform(document=document)

As a result of Step 4, the hyphens have been removed from the text.

.. code-block:: json

    {
        "content": "Lorem ipsum dolor sit amet, consectetur adipiscing
        elit, sed do... vulputate eu scelerisque felis. Faucibus nisl
        tincidunt eget nullam.\n\nFringilla phasellus faucibus scelerisque
        eleifend. Volutpat commodo... faucibus in ornare quam. Felis eget
        nunc lobortis mattis.\n\nRisus nec feugiat in fermentum
        posuere. Odio ut enim blandit volutpat... et egestas quis ipsum
        suspendisse... congue mauris rhoncus aenean.\n\nPulvinar mattis
        nunc sed blandit libero volutpat sed cras. Id
        porta... fringilla. Morbi enim nunc faucibus a.\n\nSollicitudin
        nibh sit amet commodo nulla facilisi nullam... viverra orci
        sagittis eu.\n",
        "context": {},
        "origin": null,
        "pdf_context": null,
        "title": "",
        "type": "text",
        "version": "1.0"
    }

Step 5: Create the collection
-----------------------------

It can be useful to split a document up into a collection of parts. In this
example, we will make a document from each paragraph by using ``\n\n`` to split
the document into a collection.

.. code-block:: python

    transformers.TextSplitIntoCollectionDocument(
        separator='\n\n'
    ).transform(document=document)


The collection of text documents is shown below.

.. code-block:: json

    {
        "content": [
            {
                "content": "Lorem ipsum dolor sit amet, consectetur
                adipiscing elit, sed do... vulputate eu scelerisque
                felis. Faucibus nisl tincidunt eget nullam.",
                "context": {},
                "origin": null,
                "pdf_context": null,
                "title": "",
                "type": "text",
                "version": "1.0"
            },
            {
                "content": "Fringilla phasellus faucibus scelerisque
                eleifend. Volutpat commodo... faucibus in ornare
                quam. Felis eget nunc lobortis mattis.",
                "context": {},
                "origin": null,
                "pdf_context": null,
                "title": "",
                "type": "text",
                "version": "1.0"
            },
            {
                "content": "Risus nec feugiat in fermentum posuere. Odio
                ut enim blandit volutpat... et egestas quis ipsum
                suspendisse...  congue mauris rhoncus aenean.",
                "context": {},
                "origin": null,
                "pdf_context": null,
                "title": "",
                "type": "text",
                "version": "1.0"
            },
            {
                "content": "Pulvinar mattis nunc sed blandit libero
                volutpat sed cras. Id porta... fringilla. Morbi enim nunc
                faucibus a.",
                "context": {},
                "origin": null,
                "pdf_context": null,
                "title": "",
                "type": "text",
                "version": "1.0"
            },
            {
                "content": "Sollicitudin nibh sit amet commodo nulla
                facilisi nullam... viverra orci sagittis eu.\n",
                "context": {},
                "origin": null,
                "pdf_context": null,
                "title": "",
                "type": "text",
                "version": "1.0"
            }
        ],
        "context": {},
        "origin": null,
        "title": "",
        "type": "collection",
        "version": "1.0"
    }

There are many other transformations that we can apply to text sources. You
might want to replace strings with the ``TextDocumentStringReplace``
transformer, or try more advanced concepts such as converting your document into
``passage`` documents, where you can add metadata such as ``tags`` and
``anchors``. There are also ``Conditionals`` that allow you to apply
transformers if and only if a specific condition is true. Check out our
:doc:`reference` or our other :doc:`examples` for more ideas.

.. _pipeline_example_text:

Pipeline Example: Text Documents
================================

A Python script can be used to configure a pipeline. See :doc:`pipelines` for
more details.

1. Build the framework
----------------------

We'll start by adding some Python so we can run our pipeline. We'll be focusing
on the pipeline aspect of the script, so we'll mostly gloss over this bit.

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

The manifest lists the sources that will be ingested. In this case we only have a Text file 
as source, so we create a ``manifests.sources.Text`` source and add it to the collection of sources 
contained  in the manifest. We also specify the source's standard arguments ``id``, ``pipeline``, 
``location``, and  ``destination``. 

.. code-block:: python

    def ingest(path):
        manifest = manifests.base.Manifest(
            sources=[
                manifests.sources.Text(
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
                            source='text'
                        )
                    ],
                    steps=[
                        transformers.TextSourceCreateDocument(),
                        transformers.TextDocumentHyphensRemove(),
                        transformers.TextSplitIntoCollectionDocument(
                            separator='\n\n'
                        )
                    ]
                )
            ]
        )
        return pipeline

In this example we have only one pipe, which accepts a Text file as input (specified by
``pipelines.sources.Manifest(source='text')``). The pipe sequentially applies three transformers 
to this source: ``transformers.TextSourceCreateDocument``, ``transformers.TextDocumentHyphensRemove``,
and ``transformers.TextSplitIntoCollectionDocument``.


4. Test our pipeline
---------------------

We're done! All we have to do is test it:

.. code-block:: bash

    $ python3 path/to/script.py ingest tests/data/test.txt

Note that this example pipeline has only one pipe, we can add as many as we want.

5. Export your pipeline
------------------------

Python for humans, json for computers:

.. code-block:: bash

    $ python3 path/to/script.py export

.. note::

    This prints the output to the command line, you can write the output
    to a file with:

.. code-block:: bash

    $ python3 path/to/script.py export > filename.json
