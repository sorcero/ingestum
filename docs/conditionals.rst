Conditionals Reference
======================

This is the reference page for conditionals implementation and format.

Conditional Base Class
----------------------

.. automodule:: ingestum.conditionals.base
   :exclude-members: evaluate, type, ArgumentsModel, InputsModel

AllAnd
------

.. autoclass:: ingestum.conditionals.all_and.Conditional
   :exclude-members: evaluate, ArgumentsModel, InputsModel, arguments, inputs, type

AllAttributeMatchesRegexp
-------------------------

.. autoclass:: ingestum.conditionals.all_attribute_matches_regexp.Conditional
   :exclude-members: evaluate, ArgumentsModel, InputsModel, arguments, inputs, type

AllNegate
---------

.. autoclass:: ingestum.conditionals.all_negate.Conditional
   :exclude-members: evaluate, ArgumentsModel, InputsModel, arguments, inputs, type

AllOr
-----

.. autoclass:: ingestum.conditionals.all_or.Conditional
   :exclude-members: evaluate, ArgumentsModel, InputsModel, arguments, inputs, type

CollectionHasDocumentWithConditional
------------------------------------

.. autoclass:: ingestum.conditionals.collection_has_document_with_conditional.Conditional
   :exclude-members: evaluate, ArgumentsModel, InputsModel, arguments, inputs, type

PassageHasContentPrefix
-----------------------

.. autoclass:: ingestum.conditionals.passage_has_content_prefix.Conditional
   :exclude-members: evaluate, ArgumentsModel, InputsModel, arguments, inputs, type

PassageHasTagPrefix
-------------------

.. autoclass:: ingestum.conditionals.passage_has_tag_prefix.Conditional
   :exclude-members: evaluate, ArgumentsModel, InputsModel, arguments, inputs, type

TabularHasFewerColumns
----------------------

.. autoclass:: ingestum.conditionals.tabular_has_fewer_columns.Conditional
   :exclude-members: evaluate, ArgumentsModel, InputsModel, arguments, inputs, type

TabularRowHasEmptyFrontCells
----------------------------

.. autoclass:: ingestum.conditionals.tabular_row_has_empty_front_cells.Conditional
   :exclude-members: evaluate, ArgumentsModel, InputsModel, arguments, inputs, type

TabularRowHasNValues
--------------------

.. autoclass:: ingestum.conditionals.tabular_row_has_n_values.Conditional
   :exclude-members: evaluate, ArgumentsModel, InputsModel, arguments, inputs, type

TabularRowMatches
-----------------

.. autoclass:: ingestum.conditionals.tabular_row_matches.Conditional
   :exclude-members: evaluate, ArgumentsModel, InputsModel, arguments, inputs, type

TabularRowMatchesRegexp
-----------------------

.. autoclass:: ingestum.conditionals.tabular_row_matches_regexp.Conditional
   :exclude-members: evaluate, ArgumentsModel, InputsModel, arguments, inputs, type
