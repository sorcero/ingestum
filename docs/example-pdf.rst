Example: PDF Documents
======================

In this example, we walk through an example of ingestion from an PDF document
source using the Ingestum Python libraries.

Notes:

* You'll need to follow the the :doc:`installation` if you haven't used this library before.

* To learn more about the available ingestion sources, see :doc:`sources`.

See :ref:`Pipeline Example: PDF Documents` below for a discussion of the
pipeline version of this same example.

----

The source we use in this example is a 3-page PDF document with graphics,
images, and tables.

`test.pdf <https://gitlab.com/sorcero/community/ingestum/-/blob/master/tests/data/test.pdf>`_

If all we were interested in was the text in the PDF document, we could simply
import the document and transform it into a text document. But we are interested
in ingesting the tables, images, and graphics. And along the way we'll want to
transform the representation of some of these elements. For example, we'll
convert the tables into Markdown.

The basic procedure we'll follow is to extract all of the images, tables, and
shapes, while keeping track of where (bounding box and page number) those
components were found in the original document. We then generate replacements
for those components, e.g., the Markdown tables. Finally, we swap in our
replacements and then extact the text with our replacement components in situ.

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

    pdf_source = sources.PDF(path="tests/data/test.pdf")

Step 3. Extract tables, shapes, and images
------------------------------------------

PDF document usually have three main types of content besides text:
tables, shapes (i.e. graphics), and images. We want to extract these
from the document so we can use them. The
``PDFSourceCreateTabularCollectionDocument``,
``PDFSourceShapesCreateResourceCollectionDocument``, and
``PDFSourceImagesCreateResourceCollectionDocument`` transformers each extract a
type of content and return a collection document with documents for each piece
of content. You can refer to our :doc:`transformers` for more information about
each transformer.

.. code-block:: python

    tables = transformers.PDFSourceCreateTabularCollectionDocument(
        first_page=-1,
        last_page=-1,
        options={"line_scale": 15}).transform(source=pdf_source)

Note that transformers can use placeholder values, e.g. -1 or "" which means
these will be replaced by the values given in the manifest. This way the
pipelines can be re-used with other manifests.

The output of the ``PDFSourceCreateTabularCollectionDocument`` transformer is
show below. Note that the bounding box is included in the Tabular as the
``pdf_context``.

.. code-block:: json

    {
        "content": [
            {
                "columns": 4,
                "content": [
                    [
                        "column1",
                        "column2",
                        "column3",
                        "column4"
                    ],
                    [
                        "row1",
                        "row1",
                        "row1",
                        "row1"
                    ],
                    [
                        "row2",
                        "row2",
                        "row2",
                        "row2"
                    ]
                ],
                "pdf_context": {
                    "bottom": 270,
                    "left": 56,
                    "page": 2,
                    "right": 555,
                    "top": 216
                },
                "rows": 3,
                "title": "",
                "type": "tabular",
                "version": "1.0"
            }
        ],
        "title": "Sorcero's test PDF",
        "type": "collection",
        "version": "1.0"
    }

.. code-block:: python

    shapes = transformers.PDFSourceShapesCreateResourceCollectionDocument(
        directory="tests/files",
        first_page=-1,
        last_page=-1).transform(source=pdf_source)

The output of the ``PDFSourceShapesCreateResourceCollectionDocument``
transformer is shown below. Again, note that the bounding box is included.

.. code-block:: json

    {
        "content": [
            {
                "content": "tests/files/shape.000000.1.79.561.204.655.png",
                "pdf_context": {
                    "bottom": 655,
                    "left": 79,
                    "page": 1,
                    "right": 204,
                    "top": 561
                },
                "source": "image",
                "title": "Sorcero's test PDF",
                "type": "resource",
                "version": "1.0"
            }
        ],
        "title": "Sorcero's test PDF",
        "type": "collection",
        "version": "1.0"
    }

.. code-block:: python

    images = transformers.PDFSourceImagesCreateResourceCollectionDocument(
        directory="tests/files",
        first_page=-1,
        last_page=-1).transform(source=pdf_source)

The output of the ``PDFSourceImagesCreateResourceCollectionDocument``
transformer is shown. And again, the bounding box is included.

.. code-block:: json

    {
        "content": [
            {
                "content": "tests/files/image.000000.1.54.242.316.314.png",
                "pdf_context": {
                    "bottom": 314,
                    "left": 54,
                    "page": 1,
                    "right": 316,
                    "top": 242
                },
                "source": "image",
                "title": "Sorcero's test PDF",
                "type": "resource",
                "version": "1.0"
            }
        ],
        "title": "Sorcero's test PDF",
        "type": "collection",
        "version": "1.0"
    }

Step 4: Generate replacement documents
--------------------------------------

Now that we have extracted the tables, shapes, and images, we need to generate
replacement documents that we can add to our final collection document. For
tables, this is a Markdown document, and for shapes and images, this is a
resource text document. Since each extracted content type is collection of
content documents, we'll need to use ``CollectionDocumentTransform`` to apply
the appropriate transformer to each.

.. code-block:: python

    tables_replacements = transformers.CollectionDocumentTransform(
        transformer=transformers.TabularDocumentCreateMDPassage()
    ).transform(collection=tables)

    shapes_replacements = transformers.CollectionDocumentTransform(
        transformer=transformers.ResourceCreateTextDocument()
    ).transform(collection=shapes)

    images_replacements = transformers.CollectionDocumentTransform(
        transformer=transformers.ResourceCreateTextDocument()
    ).transform(collection=shapes)

The ``tables_replacements`` output shown below is a Markdown table. The other
replacement parts are similar.

.. code-block:: json

    {
        "content": "<table>\n\n| column1 | column2 | column3 | column4 |\n
        | --- | --- | --- | --- |\n| row1 | row1 | row1 | row1 |\n
        | row2 | row2 | row2 | row2 |\n|\n\n\n</table>",
        "pdf_context": null,
        "title": "Sorcero's test PDF",
        "type": "text",
        "version": "1.0"
    }

Step 5: Consolidate extractables and replacements
-------------------------------------------------

At this point, we have six collections (three with extracted content and three
with replacement content). We'll merge the collections into an extractables
document and a replacements document with ``CollectionDocumentMerge``.

.. code-block:: python

    extractables = transformers.CollectionDocumentMerge(
        collection_1=tables,
        collection_2=shapes)
    extractables = transformers.CollectionDocumentMerge(
        collection_1=extractables,
        collection_2=images)

    replacements = transformers.CollectionDocumentMerge(
        collection_1=replacement_tables,
        collection_2=replacement_shapes)
    replacements = transformers.CollectionDocumentMerge(
        collection_1=replacements,
        collection_2=replacement_images)

Step 6: Create a text document from the parts
---------------------------------------------

Next, we'll create a text document with all of the human-readable text from the
PDF and replace the extractables we found with our replacement documents by
using the ``PDFSourceCreateTextDocumentReplacedExtractables`` transformer.

.. code-block:: python

    document = transformers.PDFSourceCreateTextDocumentReplacedExtractables(
        first_page=-1,
        last_page=-1,
        options=options).transform(pdf_source, replacements, None)

Pipeline Example: PDF Documents
===============================

A Python script can be used to configure a pipeline. See :doc:`pipelines` for
more details.

1. Build the framework
----------------------

Just like in :doc:`example-text`, we'll start by adding some Python so we can
run our pipeline. Note that we're including first page and last page arguments
so we can specify which pages of the PDF to ingest.

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


    def ingest(url, first_page, last_page):
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
        ingest_parser.add_argument('first_page', type=int)
        ingest_parser.add_argument('last_page', type=int)
        args = parser.parse_args()

        if args.command == 'export':
            output = generate_pipeline()
        else:
            output = ingest(args.url, args.first_page, args.last_page)

        print(stringify_document(output))

2. Import the source document
-----------------------------

In this pipeline, we'll be using an PDF source, so we should use
``sources.PDF(path)`` to define it. At the "Your pipeline goes here" section of
the template, add the following:

.. code-block:: python

    def ingest(url, first_page, last_page):
        manifest = manifests.base.Manifest(
            sources=[
                manifests.sources.PDF(
                    id='id',
                    pipeline='default',
                    url=url,
                    first_page=first_page,
                    last_page=last_page)])

3. Apply the transformers
-------------------------

.. code-block:: python

        pipes=[
            # Extract all tables from the PDF into
            # a collection.
            pipelines.base.Pipe(
                name="tables",
                sources=[pipelines.sources.Manifest(source="pdf")],
                steps=[
                    transformers.PDFSourceCreateTabularCollectionDocument(
                        first_page=-1, last_page=-1, options={"line_scale": 15}
                    )
                ],
            ),
            # Create a new collection with the Markdown
            # version of each of these tables.
            pipelines.base.Pipe(
                name="tables-replacements",
                sources=[
                    pipelines.sources.Pipe(
                        name="tables",
                    )
                ],
                steps=[
                    transformers.CollectionDocumentTransform(
                        transformer=transformers.TabularDocumentCreateMDPassage()  # noqa: E251
                    )
                ],
            ),
            # Extract all shapes (e.g. figures) from the PDF
            # into a collection.
            pipelines.base.Pipe(
                name="shapes",
                sources=[pipelines.sources.Manifest(source="pdf")],
                steps=[
                    transformers.PDFSourceShapesCreateResourceCollectionDocument(  # noqa: E251
                        directory="output", first_page=-1, last_page=-1
                    )
                ],
            ),
            # Create a new collection with text references
            # (e.g. file://shape.png) for each shape.
            pipelines.base.Pipe(
                name="shapes-replacements",
                sources=[pipelines.sources.Pipe(name="shapes")],
                steps=[
                    transformers.CollectionDocumentTransform(
                        transformer=transformers.ResourceCreateTextDocument()
                    )
                ],
            ),
            # Extract all images (e.g. PNG images) from the
            # PDF into a collection.
            pipelines.base.Pipe(
                name="images",
                sources=[pipelines.sources.Manifest(source="pdf")],
                steps=[
                    transformers.PDFSourceImagesCreateResourceCollectionDocument(  # noqa: E251
                        directory="output", first_page=-1, last_page=-1
                    )
                ],
            ),
            # Create a new collection with text references
            # (e.g. file://image.png) for every image.
            pipelines.base.Pipe(
                name="images-replacements",
                sources=[pipelines.sources.Pipe(name="images")],
                steps=[
                    transformers.CollectionDocumentTransform(
                        transformer=transformers.ResourceCreateTextDocument()
                    )
                ],
            ),
            # Merge all previously extracted tables, shapes
            # and images (extractables) into a single
            # collection.
            pipelines.base.Pipe(
                name="extractables",
                sources=[
                    pipelines.sources.Pipe(name="tables"),
                    pipelines.sources.Pipe(name="shapes"),
                ],
                steps=[transformers.CollectionDocumentMerge()],
            ),
            # Merge all previously extracted tables, shapes
            # and images (extractables) into a single
            # collection.
            pipelines.base.Pipe(
                name="extractables",
                sources=[
                    pipelines.sources.Pipe(name="extractables"),
                    pipelines.sources.Pipe(name="images"),
                ],
                steps=[transformers.CollectionDocumentMerge()],
            ),
            # Merge all previously created Markdown and text
            # references (replacements) into a single
            # collection.
            pipelines.base.Pipe(
                name="replacements",
                sources=[
                    pipelines.sources.Pipe(name="tables-replacements"),
                    pipelines.sources.Pipe(name="shapes-replacements"),
                ],
                steps=[transformers.CollectionDocumentMerge()],
            ),
            # Merge all previously created Markdown and text
            # references (replacements) into a single
            # collection.
            pipelines.base.Pipe(
                name="replacements",
                sources=[
                    pipelines.sources.Pipe(name="replacements"),
                    pipelines.sources.Pipe(name="images-replacements"),
                ],
                steps=[transformers.CollectionDocumentMerge()],
            ),
            # Extract all human-readable text fom the PDF, except
            # for the extractables, and replace these with Markdown
            # tables and text references.
            pipelines.base.Pipe(
                name="text",
                sources=[
                    pipelines.sources.Manifest(source="pdf"),
                    pipelines.sources.Pipe(name="extractables"),
                    pipelines.sources.Pipe(name="replacements"),
                ],
                steps=[
                    transformers.PDFSourceCreateTextDocumentReplacedExtractables(  # noqa: E251
                        first_page=-1, last_page=-1
                    ),
                ],
            )
        ]

4. Test your pipeline
---------------------

We're done! All we have to do is test it::

    $ python3 path/to/script.py ingest file://tests/data/test.pdf 1 3

This tutorial gave some examples of what you can do with a PDF source, but it's
certainly not exhaustive. Sorcero provides a variety of tools to deal with
PDF documents. Check out our :doc:`reference` or our other :doc:`examples` for
more ideas.

5. Export your pipeline
------------------------

Python for humans, json for computers::

    $ python3 path/to/script.py export
