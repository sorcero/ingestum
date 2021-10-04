# ingestum-toolbox

If you're running Fedora, [Toolbox](https://github.com/containers/toolbox) makes it easy to use a containerized environment for everyday software development. Therefore, we provide a toolbox-enabled container to get started with Ingestum a lot easier and faster.

## Setup

```
$ sudo dnf -y install toolbox
```

## Build

```
$ podman build . -t ingestum-toolbox:latest
$ toolbox create -c ingestum-toolbox -i ingestum-toolbox
```

## Run

```
$ toolbox enter ingestum-toolbox
```
