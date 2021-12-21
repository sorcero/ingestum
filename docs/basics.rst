Ingestion Basics
================

There are six major concepts which are key to understanding the ingestion
process facilitated by `Ingestum`: `Sources`, `Documents`, `Transformers`,
`Conditionals`, `Pipelines`, and `Manifests`.

Sources
-------

Ingestion always starts with a source file. These files can be found in different
formats such as images, audios, text files, spreedsheets, etc. But, in their native format, they
may not be directly amenable to downstream processing. In order to use them in the ingestion process,
the first step is always to convert these `Sources` into `Ingestum Documents`.
You can find a list of all the types of `Sources` that `Ingestum` currently works with in
the :doc:`sources` page.

Documents
---------

In almost every ingestion process, `Sources` are converted to `Documents`, which
are standardized formats that the remainder of the `Ingestum Pipeline`
recognizes. They serve as intermediaries to which Transformers (more on those in the next section) are applied.
After being operated upon by multiple Transformers, the resulting Document can be passed on to other processes.
Several types of Documents may be employed in a single ingestion process, including tabular documents for
storing table-like data, passage documents for storing text-like data, and aptly named collection documents,
which are used for collections of documents. You can find a list of all the types of Documents used by Ingestum,
with examples, on the :doc:`documents` page.

Transformers
------------

`Transformers` are at the core of `Ingestum`. Each `Transformer` receives an
input `Source` or `Document` along with configuration options. The `Transformer`
applies a specific operation on its input and returns an output `Document`. You
can find a list of `Transformers`, with examples, on the
:doc:`transformers` page.

Pipelines
---------

A `Pipe` is a workflow that describes a sequence of transformers to be applied,
where the output of one transformer becomes the input to the next transformer.
A `Pipeline` consists of a collection of `Pipes`. See :doc:`pipeline-details`
for more details. You can also see this in action in the :doc:`examples` page.
And there is a :doc:`pipelines` available as well.

Conditionals
------------

`Conditionals` refer to logical conditions that can modify the behavior of a
`Pipeline`. `Transformers` inside of a `Conditional` will only perform their
operation if a certain condition is met. By combining `Transformers` and
`Conditionals`, `Pipelines` can be built to handle some of the complexities
often found in documents. For example, you may only want to apply a transformer
when a regular expression matches a specific condition. You can find a list of
all `Conditionals` with examples in the :doc:`conditionals` page.

Manifests
---------

A `Manifest` describes what `Sources` need to be ingested, what `Pipelines` to
apply to do that ingestion, and any parameters associated with the `Pipelines`.
For example, take this PDF file and apply that pipeline to extract plain text
within this specific page range. Each combination of `Source` file, `Pipeline`
name and its set of parameters is called a `Manifest Source`. One single
`Manifest` can include many `Manifest Sources`. See :doc:`manifest-details` for
more details. Also see the :doc:`manifests` page.
