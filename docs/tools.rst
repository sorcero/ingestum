Tools
=====

There are several command-line tools to make it easier to use Ingestum. All of these tools must be run in the Ingestum environment.

ingestum-manifest
-----------------

This command-line utility is used to run an Ingestum manifest.

.. code-block:: bash

    $ ingestum-manifest
      usage: ingestum-manifest [-h] [--pipelines PIPELINES] [--artifacts ARTIFACTS] [--workspace WORKSPACE] [--instrumentation [{measure-memory}]] manifest

* The :code:`manifest` mandatory argument is used to specify the manifest to be processed.
* The :code:`--pipelines` mandatory argument is used to specify a path to the pipeline used in the manifest.
* The :code:`--artifacts` optional argument is used to specify a path for any artifacts (images, etc.) output from the ingestion process.
* The :code:`--workspace` optional argument is used to specify a path for the document output from the ingestion process.
* The :code:`--instrumentation` optional argument is used to profile memory usage during the ingestion process.

Example:

.. code-block:: bash

    $ ingestum-manifest manifest.json --pipelines sorcero-ingestion-scripts/pipelines

ingestum-generate-manifest
--------------------------

This command-line utility is used to generate an Ingestum manifest.

.. code-block:: bash

    $ ingestum-generate-manifest
      usage: ingestum-generate-manifest [-h] [--id ID] [--pipeline PIPELINE] [--manifest MANIFEST] source

* The :code:`source` mandatory argument is used to specify the manifest source to be used.
* The :code:`--id` optional argument is used to specify the manifest source ID. If not specified, a random ID will be auto-generated.
* The :code:`--pipelines` argument is used to specify the name of a pipeline to used in the manifest.
* The :code:`--manifest` optional argument is used to specify a path of an existing manifest to append a new manifest source.

**The source itself is parsed for additional arguments.**

Example:

.. code-block:: bash

    $ ingestum-generate-manifest pubmed
      usage: ingestum-generate-manifest [-h] [--id ID] [--pipeline PIPELINE] [--manifest MANIFEST] [--terms TERMS [TERMS ...]] --articles ARTICLES [--hours HOURS] [--from_date FROM_DATE] [--to_date TO_DATE] source

    $ ingestum-generate-manifest pubmed --terms eye --articles 1500 --hours 168 --pipeline pipeline_pubmed_publication --id test_eye_query

ingestum-pipeline
-----------------

This command-line utility is used to run an Ingestum pipeline.

.. code-block:: bash

    $ ingestum-pipeline
      usage: ingestum-pipeline [-h] [--workspace WORKSPACE] [--artifacts ARTIFACTS] pipeline

* The :code:`pipeline` mandatory argument is used to specify the pipeline to be ran.
* The :code:`--workspace` optional argument is used to specify a path for the document output from the ingestion process.
* The :code:`--artifacts` optional argument is used to specify a path for any artifacts (images, etc.) output from the ingestion process.

**The pipeline itself is parsed for additional arguments.**

Example:

.. code-block:: bash

    $ ingestum-pipeline pipeline_pubmed_publication.json 
      usage: ingestum-pipeline [-h] [--workspace WORKSPACE] [--artifacts ARTIFACTS] [--terms TERMS [TERMS ...]] --articles ARTICLES [--hours HOURS] [--from_date FROM_DATE] [--to_date TO_DATE] [--full_text] pipeline

    $ ingestum-pipeline pipeline_pubmed_publication.json --term eye --articles 1500 --hours 168

ingestum-envelope
-----------------

This command-line utility is used to run an Ingestum envelope.

.. code-block:: bash

    $ ingestum-envelope
      usage: ingestum-envelope [-h] [--pipelines PIPELINES] [--artifacts ARTIFACTS] [--workspace WORKSPACE] [--results RESULTS] envelope

* The :code:`envelope` mandatory argument is used to specify the envelope to be processed.
* The :code:`--pipelines` optional argument is used to specify a path to the pipeline used in the manifest.
* The :code:`--artifacts` optional argument is used to specify a path for any artifacts (images, etc.) output from the ingestion process.
* The :code:`--workspace` optional argument is used to specify a path for the document output from the ingestion process.
* The :code:`--results` optional argument is used to specify a path for the references output to be written to. Without this argument, the references output will be directed to the standard output.

Example:

.. code-block:: bash

    $ ingestum-envelope envelope.json --results results.json

ingestum-merge
--------------

This command-line utility is used to merge multiple documents into one document.

.. code-block:: bash

    $ ingestum-merge
      usage: ingestum-merge [-h] [--output OUTPUT] documents [documents ...]

* The :code:`documents` mandatory argument is used to specify the list of documents to be processed.
* The :code:`--output` mandatory argument is used to specify the path to the output merged document.

Example:

We could merge results from multiple PubMed searches into one document.

.. code-block:: bash

    $ ingestum-merge document1.json document2.json document3.json --output document4.json

ingestum-migrate
----------------

This command-line utility is used to migrate multiple documents from earlier versions of Ingestum to the current document format (as on occasion, we add new fields to the document format).

.. code-block:: bash

    $ ingestum-migrate
      usage: ingestum-migrate [-h] documents [documents ...]

* The :code:`documents` mandatory argument is used to specify the list of documents to be processed.

**The documents are updated in place.**

Example:

.. code-block:: bash

    $ ingestum-migrate tests/output/*.json

ingestum-inspect
----------------

This command-line utility is used to extract the content from an ingested document.

.. code-block:: bash

    $ ingestum-inspect
      usage: ingestum-inspect [-h] document

* The :code:`document` mandatory argument is used to specify the path of the document to be processed.

Example:

.. code-block:: bash

    $ ingestum-inspect document.json

