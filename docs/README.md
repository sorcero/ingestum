## Ingestum Documentation

Dependencies for compiling the documentation are in `docs/requirements.txt`.

```
$ pip install -r docs/requirements.txt
```

You'll also need to install [Make](https://www.gnu.org/software/make/) if it's
not already installed.

To compile:

```
pip install -r docs/requirements.txt
```

To build:

```
sphinx-build -b html docs public
```

You can then access the docs locally by loading the `index.html` file
in the `public` directory into a web browser.

## Disclaimer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the [GNU
Lesser General Public License](LICENSE) for more details.
