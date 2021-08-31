Manifest Details
================

A `Manifest` is a list of sources to be ingested. A `Manifest` is also used to
couple a `Source` with a `Pipeline`. Also, within a `Manifest`, arguments to
`Transformers`, such as ``first-page``, can be set.

.. code-block:: json

    {
        "sources": [
            {
                "type": "text",
                "id": "636678fd-f16c-4c1c-81ec-d78f49aadfe3",
                "pipeline": "pipeline_text",
                "path": "file://tests/data/test.txt"
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
    $ ingestum-manifest tests/pipelines/manifest_twitter.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_xml.json --pipelines=tests/pipelines --workspace=workspace

Inspecting the results
----------------------

Use ``ingestum-inspect`` to examine a document created by the pipeline:

.. code-block:: bash

    $ ingestum-inspect workspace/c124d591-eebd-4796-8f3b-1fed90a5ebe8/output/document.json
