Manifest Details
================

A `Manifest` is a list of sources to be ingested and is used to couple a `Source` with
a `Pipeline`, i.e each `Source` on the list can specify wich `Pipeline` to apply.
Also, within a `Manifest`, arguments to `Transformers`, such as
``first_page`` and ``last_page``, can be set.

.. code-block:: json

    {
        "sources": [
            {
                "type": "pdf",
                "id": "c124d591-eebd-4796-8f3b-1fed90a5ebe8",
                "pipeline": "pipeline_pdf",
                "location": {
                    "type": "local",
                    "path": "tests/data/test.pdf"
                },
                "destination": {
                    "type": "local",
                    "directory": "/tmp/ingestum/destinations/"
                },
                "first_page": 1,
                "last_page": 3
            }
        ]
    }


Running a manifest from the command line
----------------------------------------

In the ``tests/pipelines`` directory, you'll find numerous manifest
examples to explore and use for the basis of your own projects:

.. code-block:: bash

    $ ingestum-manifest tests/pipelines/manifest_annotation.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_audio.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_csv.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_docx.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_xls.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_html.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_image.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_pdf.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_text.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_twitter_form.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_xml.json --pipelines=tests/pipelines --workspace=workspace

Inspecting the results
----------------------

Use ``ingestum-inspect`` to examine a document created by the pipeline:

.. code-block:: bash

    $ ingestum-inspect workspace/c124d591-eebd-4796-8f3b-1fed90a5ebe8/output/document.json

Generating a manifest from the command line
-------------------------------------------

Use ``ingestum-generate-manifest`` to create a manifest:

.. code-block:: bash
    $ ingestum-generate-manifest --pipeline pipeline_pdf_example --first_page 1 --last_page 5

You can also extend an existing manifest by adding the parameter ``--manifest`` along with its name.
