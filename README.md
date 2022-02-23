# [WIP] Tempren - template-based batch file renaming utility
[![Build Status](https://travis-ci.org/idle-code/tempren.svg?branch=develop)](https://travis-ci.org/idle-code/tempren)
[![codecov](https://codecov.io/gh/idle-code/tempren/branch/develop/graph/badge.svg?token=1CR2PX6GYB)](https://codecov.io/gh/idle-code/tempren)

**This project is currently in a Work-In-Progress stage so if you are looking for working solution... keep looking.**

TODO: Summary

## Features
- Template-based filename/path generation
- Configurable file selection
- Metadata-based sorting


## Install
```console
$ pip install [--user] poetry
$ poetry install
```

## TODO: Usage

**Note: When playing with tempren make sure to use `--dry-run` (`-d`) flag so that the actual files are not accidentally changed.**

Tempren have two main modes of operation: **name** and **path**.

In the **name** mode, the template is used for filename generation only.
This is useful if you want to operate on files specified on the command line or in a single directory.

With **path** mode, the template generates a whole path (relative to the input directory).
This way you can sort files into dynamically generated catalogues.
### Template syntax
#### Pipe list sugar
### Name mode
### Path mode
### Filtering
#### Glob filtering
#### Regex filtering
#### Template filtering
#### Case sensitiveness and filter inversion
### Sorting

### Testing
Tests are written with a help of [pytest](https://docs.pytest.org/en/latest/). Just enter repository root and run:
```console
$ pytest
```

## Contribution
Code conventions are enforced via [pre-commit](https://pre-commit.com/). It is listed in development depenencies so if you are able to run tests - you should have it installed too.
To get started you will still need to install git hooks via:
```console
$ pre-commit install
```
Now every time you invoke `git commit` a series of cleanup scripts will run and modify your patchset.

### TODO: Tags development
