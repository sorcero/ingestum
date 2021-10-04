# ingestum-docker

_Ingestum_ was developed for _Ubuntu 20.04_ (_Linux_). It has quite a few system dependencies and relies on a list of Python libraries. It can be set up to work on other operating systems
(especially ones that are _Unix-based_), but there could be trouble setting it up (e.g. conflicting with already installed packages) or some features wouldn't work.

Therefore, a containerized environment makes it easy for everyday for everyday software development. We provide a _Docker_-based setup to get started with _Ingestum_.

## Requirements

An installation of [Docker](https://www.docker.com/get-started) - _Docker Desktop_ (for _Windows_,
_Mac_) or _Docker Engine_ (for _Linux_) is required.

_Docker_ might need _root_ (_administrator_) access to run.

## Setup

For the first use, you'll need to build the _OCI_ image our setup uses. The `Dockerfile` contains
the instructions needed to build it. Either, download it as a single file, or download this whole
repository.

There is also a `docker-compose.yml` file which provides an easy way to build the image and run a
container using it.

### Build

#### With `docker-compose` (recommended)

```bash
$ docker-compose build
```

#### Or, without `docker-compose`

```bash
$ docker build -t ingestum:latest .
```

### Run

#### With `docker-compose` (recommended)

```bash
$ docker-compose up
```

This also binds a directory `/ingestum` inside the container with the directory the
`docker-compose.yml` (and `Dockerfile`) file is present in. This opens up the possibility of sharing
the scripts and source files between the container and the host system. In this way, the container
acts as a sandbox installed with _Ingestum_ and its dependencies, and your host applications (e.g.
code editor, PDF viewer) have access to the scripts you write, or your source files.

To shut down the container, in a separate terminal window run

```bash
$ docker-compose down
```

#### Or, without `docker-compose`

```bash
$ docker run -it --rm --name ingestum --mount type=bind,source=/absolute/path/on/host/,destination=/app ingestum:latest
```

#### To simply spawn a container and explore

```bash
$ docker run -it --rm --name ingestum ingestum:latest
```

## Miscellaneous

We have mentioned about _Toolbox_ earlier here. You can pick either of our two setups:
_Toolbox_-based or _Docker_-based. If you want to learn more about _Toolbox_ and the differences
with _Docker_, there is an article about
[Fedora Toolbox - Under the hood](https://debarshiray.wordpress.com/2019/01/21/fedora-toolbox-under-the-hood/#:~:text=Every%20time%20you%20invoke%20the,or%20be%20run%20as%20root.&text=So%2C%20instead%20of%20using%20Docker,drop%2Din%20replacement%20for%20Docker.) you can read.
