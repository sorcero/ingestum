Pipelines Reference
===================

This is the reference page for pipelines implementation and format.

Pipe Base Class
---------------

.. autoclass:: ingestum.pipelines.base.Pipe
    :exclude-members: name, sources, steps, type

Pipeline Sources Base Class
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.pipelines.sources.base.BaseSource
    :exclude-members: type

Pipeline Sources Manifest
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.pipelines.sources.manifest.Source
    :exclude-members: source, get_source_class, type

Pipeline Sources Nothing
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.pipelines.sources.nothing.Source
    :exclude-members: type

Pipeline Sources Pipe
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ingestum.pipelines.sources.pipe.Source
    :exclude-members: type, name


Pipeline Base Class
-------------------

.. autoclass:: ingestum.pipelines.base.Pipeline
    :exclude-members: name, pipes, _treat_sources, run, type
