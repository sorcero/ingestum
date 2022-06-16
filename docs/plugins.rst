Plugins
=======

Plugins are custom Sources, Documents, Transformers, and Conditionals
that can be added to the ingestion process without making
modifications to the library.

Plugins are pulled from the directory specified in the environment
variable `INGESTUM_PLUGINS_DIR`. By default, `~/.ingestum/plugins` is used.

Multiple plugins directories can be specified using the separator ``:`` as follows:

.. code-block:: bash

    $ export INGESTUM_PLUGINS_DIR=/path/to/plugins1:/path/to/plugins2

Installation
------------

Once Ingestum is installed and `INGESTUM_PLUGINS_DIR` is set, use the following
command to install all plugins requirements.

.. code-block:: bash

    $ ingestum-install-plugins

Plugins directory structure
---------------------------

The organization of the plugins directory is as follows::

    plugins/
    ├── my_first_plugin
    │   ├──  plugin
    │   │   ├── __init__.py
    │   │   └── transformers
    │   │       ├── __init__.py
    │   │       └── my_first_plugin_transformer.py
    │   ├── tests
    │   │   ├── data
    │   │   │   └── test.txt
    │   │   ├── input
    │   │   │   └── input_document.json
    │   │   ├── output
    │   │   │   └── output_document.json
    │   │   └── test_plugin.py
    │   ├── README.md
    │   └── requirements.txt
    │     
    └── my_second_plugin
        ├──  plugin
        │   ├── __init__.py
        │   ├── manifests
        │   │   ├── __init__.py
        │   │   └── sources
        │   │       ├── __init__.py
        │   │       └── my_second_plugin_manifest_source.py
        │   ├── sources
        │   │   ├── __init__.py
        │   │   └── my_second_plugin_source.py
        │   └── transformers
        │       ├── __init__.py
        │       └── my_second_plugin_transformer.py
        ├── scripts
        │   └── pipeline_my_second_plugin.py
        ├── tests
        │   ├── pipelines
        │   │   └── pipeline_my_second_plugin.json
        │   └── test_plugin.py
        ├── README.md
        └── requirements.txt

Plugins imports
---------------

There are some minor differences in the imports used by the
plugins. Path names need to be absolute rather than relative:

.. code-block:: python

    from .. import documents

becomes

.. code-block:: python

    from ingestum import documents

Plugins pytest
-----------------

We encourage you to add pytest tests for your plugin. ``tests/test_plugin.py``
will be run as part of ``qa.sh``.

Plugins requirements
--------------------

You must include ingestum in your ``requirements.txt`` file. The
specification should match the version of ingestum you are running. For
example::

    git+https://gitlab.com/sorcero/community/ingestum.git@master#egg=ingestum

.. warning::

    When defining a new transformer, you might get an `AttributeError` if you 
    try to do the following:

    .. code-block:: python
        
        from ingestum import transformers

        class NewTransformer(transformers.some_transformer.Transformer):
        ...

    This throws an error due to a circular import.

    This can be fixed by importing the specific transformer, instead of the whole module:

    .. code-block:: python

        from ingestum import transformers.some_transformer.Transformer as OldTransformer

        class NewTransformer(OldTransformer):
        ...
    
    This also applies for sources, documents, and manifests definitions.
