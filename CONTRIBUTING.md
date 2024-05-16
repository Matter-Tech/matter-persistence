# Contributing

Make sure you have all supported python versions installed in your machine:

* 3.10
* 3.11
* 3.12

## Install hatch in your system

```https://hatch.pypa.io/latest/install/```

## Create the environment

```console
hatch env create
```

## Install pre-commit hook

```console
hatch shell && pre-commit install
```

Do your changes...

## Run the tests

```console
hatch run test
```

The command above will run the tests against all supported python versions
installed in your machine. For testing in other operating system you may use the
configured CI in github.

## Formatting your code
    
```console
hatch run fmt
```

## Run the linter

```console
hatch run lint
```

## Run static type checker

```console
hatch run typing
```