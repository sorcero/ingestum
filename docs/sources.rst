Sources Reference
=================

This is the reference page for `Ingestum Sources` implementation and format.

Source Base Class
-----------------

.. autoclass:: ingestum.sources.base.BaseSource
   :exclude-members: Config, type

Source Local Class
------------------

.. autoclass:: ingestum.sources.local.LocalSource
   :exclude-members: path, type

Audio
-----

.. autoclass:: ingestum.sources.audio.Source
   :exclude-members: type

Biorxiv
-------

.. autoclass:: ingestum.sources.biorxiv.Source
   :exclude-members: type

CSV
---

.. autoclass:: ingestum.sources.csv.Source
   :exclude-members: separator, type

Document
--------

.. autoclass:: ingestum.sources.document.Source
   :exclude-members: type

DOCX
----

.. autoclass:: ingestum.sources.docx.Source
   :exclude-members: type

Email
-----

.. autoclass:: ingestum.sources.email.Source
   :exclude-members: host, port, user, password, type

EuropePMC
---------

.. autoclass:: ingestum.sources.europepmc.Source
   :exclude-members: type

HTML
----

.. autoclass:: ingestum.sources.html.Source
   :exclude-members: type

Image
-----

.. autoclass:: ingestum.sources.image.Source
   :exclude-members: type


LitCovid
--------

.. autoclass:: ingestum.sources.litcovid.Source
   :exclude-members: type

PDF
---

.. autoclass:: ingestum.sources.pdf.Source
   :exclude-members: decode, type

ProQuest
--------

.. autoclass:: ingestum.sources.proquest.Source
   :exclude-members: endpoint, token, type

PubMed
--------

.. autoclass:: ingestum.sources.pubmed.Source
   :exclude-members: tool, email, type

Reddit
--------

.. autoclass:: ingestum.sources.reddit.Source
   :exclude-members: client_id, client_secret, user_agent, get_reddit, type

Text
----

.. autoclass:: ingestum.sources.text.Source
   :exclude-members: type

Twitter
-------

.. autoclass:: ingestum.sources.twitter.Source
   :exclude-members: consumer_key, consumer_secret, get_api, type

XLS
---

.. autoclass:: ingestum.sources.xls.Source
   :exclude-members: type

XML
---

.. autoclass:: ingestum.sources.xml.Source
   :exclude-members: type
