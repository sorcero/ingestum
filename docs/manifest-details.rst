Manifest Details
================

A manifest is a list of sources to be ingested. A manifest is also
used to couple a source with a pipeline. Also, within a manifest
arguments to transformers, such as ``first-page``, can be set.

.. code-block:: json

    {
        "sources": [
            {
                "type": "text",
                "id": "636678fd-f16c-4c1c-81ec-d78f49aadfe3",
                "pipeline": "pipeline_text",
                "url": "file://tests/data/test.txt"
            }
        ]
    }

Running a manifest from the command line
----------------------------------------

In the ``tests/pipelines`` directory, you'll find numerous manifest
examples to explore and use for the basis of your own projects::

    $ ingestum-manifest tests/pipelines/manifest_annotation.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_audio.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_csv.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_excel.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_html.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_pdf.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_twitter.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_text.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_image.json --pipelines=tests/pipelines --workspace=workspace
    $ ingestum-manifest tests/pipelines/manifest_xml.json --pipelines=tests/pipelines --workspace=workspace

Inspecting the results
----------------------

Use ingestum-inspect to examine a document created by the pipeline::

    $ ingestum-inspect workspace/c124d591-eebd-4796-8f3b-1fed90a5ebe8/output/document.json
