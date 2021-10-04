Manifests Reference
===================

This is the reference page for manifests implementation and format.

Manifest Base Class
-------------------

.. autoclass:: ingestum.manifests.base.Manifest
   :exclude-members: sources, type

Manifest Source Base Class
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.base.BaseSource
   :exclude-members: id, pipeline, destination, get_source, type

Manifest Source Audio
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.audio.Source
   :exclude-members: get_source, preprocess_audio, type

Manifest Source Biorxiv
~~~~~~~~~~~~~~~~~~~~~~~
.. autoclass:: ingestum.manifests.sources.biorxiv.Source
   :exclude-members: query, articles, hours, from_date, to_date, repo, filters, get_source, type

Manifest Source CSV
~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.csv.Source
   :exclude-members: get_source, type

Manifest Source Document
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.document.Source
   :exclude-members: get_source, type

Manifest Source DOCX
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.docx.Source
   :exclude-members: get_source, type

Manifest Source Email
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.email.Source
   :exclude-members: get_source, hours, sender, subject, body, type

Manifest Source EuropePMC
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.europepmc.Source
   :exclude-members: get_source, query, articles, hours, from_date, to_date, type

Manifest Source HTML
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.html.Source
   :exclude-members: get_source, url, target, type

Manifest Source Image
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.image.Source
   :exclude-members: get_source, type

Manifest Source LitCovid
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.litcovid.Source
   :exclude-members: get_source, query_string, sort, type

Manifest Source Located
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.located.Source
   :exclude-members: get_source, location, type

Manifest Source PDF
~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.pdf.Source
   :exclude-members: get_source, first_page, last_page, type

Manifest Source ProQuest
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.proquest.Source
   :exclude-members: get_source, query, databases, articles, type

Manifest Source PubMed
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.pubmed.Source
   :exclude-members: get_source, terms, articles, hours, from_date, to_date, type

Manifest Source Reddit
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.reddit.Source
   :exclude-members: get_source, search, subreddit, sort, type

Manifest Source Text
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.text.Source
   :exclude-members: get_source, type

Manifest Source Twitter
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.twitter.Source
   :exclude-members: get_source, search, tags, count, sort, type

Manifest Source XLS
~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.xls.Source
   :exclude-members: get_source, type

Manifest Source XML
~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.xml.Source
   :exclude-members: get_source, type

Manifest Source Credentials Base Class
--------------------------------------

.. autoclass:: ingestum.manifests.sources.credentials.base.BaseCredential
    :exclude-members: type

Manifest Source Credentials Headers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.credentials.headers.Credential
   :exclude-members: content, type

Manifest Source Credentials OAuth2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.credentials.oauth2.Credential
   :exclude-members: token, type

Manifest Source Destinations Base Class
--------------------------------------

.. autoclass:: ingestum.manifests.sources.destinations.base.BaseDestination
   :exclude-members: _generate_unique_name, _artifactify, _documentify, dump, store, type

Manifest Source Destinations Google Datalake
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.destinations.google_datalake.Destination
   :exclude-members: project, bucket, prefix, credential, store, type

Manifest Source Destinations Local
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.destinations.local.Destination
   :exclude-members: directory, store, type

Manifest Source Destinations Remote
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.destinations.remote.Destination
   :exclude-members: url, credential, store, type

Manifest Source Destinations Void
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.destinations.local.Destination
   :exclude-members: url, credential, store, type, directory

Manifest Source Locations Base Class
------------------------------------

.. autoclass:: ingestum.manifests.sources.locations.base.BaseLocation
   :exclude-members: fetch, type

Manifest Source Locations Google Datalake
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.locations.google_datalake.Location
   :exclude-members: fetch, project, bucket, path, credential, type

Manifest Source Locations Local
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.locations.local.Location
   :exclude-members: fetch, path, type

Manifest Source Locations Remote Video
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.locations.remote_video.Location
   :exclude-members: fetch, url, type

Manifest Source Locations Remote
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.manifests.sources.locations.remote.Location
   :exclude-members: fetch, url, credential, type