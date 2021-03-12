Plugins
=======

Plugins are custom Sources, Documents, Transformers, and Conditionals
that can be added to the ingestion process without making
modifications to the library.

Plugins are pulled from the directory specified in the environment
variable `INGESTUM_PLUGINS_DIR`. By default, `~/.ingestum/plugins` is used.

Plugins directory structure
---------------------------

The organization of the plugins directory is as follows::

    plugins/
    ├── my_first_plugin
    │   ├── __init__.py
    │   ├── requirements.txt
    │   ├── tests
    │   │   ├── input
    │   │   │   └── input_document.json
    │   │   ├── output
    │   │   │   └── output_document.json
    │   │   └── plugin.py
    │   └── transformers
    │       ├── __init__.py
    │       └── my_first_plugin.py
    └── my_second_plugin
        ├── __init__.py
        ├── requirements.txt
        ├── tests
        │   ├── input
        │   │   └── input_document.json
        │   ├── output
        │   │   └── output_document.json
        │   └── plugin.py
        └── sources
            ├── __init__.py
            └── my_second_plugin.py

Plugins imports
---------------

There are some minor differences in the imports used by the
plugins. Path names need to be absolute rather than relative:

.. code-block:: python

    from .. import documents

becomes

.. code-block:: python

    from ingestum import documents

Plugins unittests
-----------------

We encourage you to add unittests for your plugin. ``tests/plugin.py``
will be run as part of ``qa.sh``.

Plugins requirements
--------------------

You must include ingestum in your ``requirements.txt`` file. The
specification should match the version of ingestum you are running. For
example::

    git+https://gitlab.com/sorcero/community/ingestum.git@master#egg=ingestum
