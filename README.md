# ingestum

[![Ingestum](docs/ingestum.png)](https://gitlab.com/sorcero/community/ingestum)

This library is used to transform common content formats into
documents that can be used by other pipelines and processes,
e.g. document comparison, search, or tagging. For example, taking an
HTML file, removing all of its HTML tags, and extracting only the
human-visible text. The resulting document is indistinguishable from
any other regular text document. This transformation process called
`ingestion`.

To achieve this, the library relies on four main concepts:

1. [Sources](ingestum/sources/base.py), which refers to the common content formats that can be taken into the ingestion process, e.g. PDF, HTML, PNG, WAV, or feeds such as Twitter, ProQuest, or email.
2. [Documents](ingestum/documents/base.py), which refers to the final and intermediary state of an input _source_ during the ingestion process. Documents can be transformed into other types of documents, many times, until is ready for further processing.
3. [Transformers](ingestum/transformers/base.py), which refers to a single transformation function that can be applied to each content type, e.g. removing all hyphens from a text document, or removing all `<sub>` tags from a HTML document.
4. [Conditionals](ingestum/conditionals/base.py), which refers to a logic conditional operation that can be use to modify the behavior of a transformer.

## Installation

Follow the [Installation Guide](https://sorcero.gitlab.io/community/ingestum/installation.html) for instructions.

## Documentation

Follow the compiled [Documentation](https://sorcero.gitlab.io/community/ingestum/) for introduction, guides, examples, and references.

## Disclaimer

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the [GNU Lesser General Public License](LICENSE) for more details.
