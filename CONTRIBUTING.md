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

Do your changes...

## Run the tests

```console
hatch run test
```

The command above will run the tests against all supported python versions
installed in your machine. For testing in other operating system you may use the
configured CI in github. 

## Run the tests in a docker container (For testing Postgres integration)

It is assumed you have docker installed and running in your machine.
```console
hatch run dockerized:test
```

## Formatting your code
    
```console
hatch run fmt
```

## Run the linters

```console
hatch run lint
```
