Pipeline Details
================

`Pipelines` describe how `Sources` are ingested. A pipeline consists of a
collection of `Pipes`, each of which contains a series of steps that define the
order in which transformers are applied.

.. code-block:: json

    {
        "name": "pipeline_text",
        "pipes": [
            {
                "name": "plain",
                "sources": [
                    {
                        "type": "manifest",
                        "source": "text"
                    }
                ],
                "steps": [
                    {
                        "type": "text_source_create_document",
                        "arguments": {}
                    }
                ]
            }
        ]
    }

Running a pipeline from the command line
----------------------------------------

In ``tests/pipelines`` you'll find some example pipelines that you can use as a
starting point for designing your own pipelines.

To run a pipeline from the command line:

.. code-block:: bash

    $ ingestum-pipeline tests/pipelines/pipeline_audio.json --path tests/data/test.wav
    $ ingestum-pipeline tests/pipelines/pipeline_csv.json --path tests/data/test.csv
    $ ingestum-pipeline tests/pipelines/pipeline_docx.json --path tests/data/test.docx
    $ ingestum-pipeline tests/pipelines/pipeline_xls.json --path tests/data/test.xlsx
    $ ingestum-pipeline tests/pipelines/pipeline_html.json --path tests/data/test.html --target body
    $ ingestum-pipeline tests/pipelines/pipeline_image.json --path tests/data/test.jpg
    $ ingestum-pipeline tests/pipelines/pipeline_pdf.json --path tests/data/test.pdf --first_page 1 --last_page 3
    $ ingestum-pipeline tests/pipelines/pipeline_reddit.json --search "python" --subreddit "learnpython"
    $ ingestum-pipeline tests/pipelines/pipeline_text.json --path tests/data/test.txt
    $ ingestum-pipeline tests/pipelines/pipeline_twitter_form.json --search "sorcero"
    $ ingestum-pipeline tests/pipelines/pipeline_xml.json --path tests/data/test.xml
