# Tempren - template-based file renaming utility

![run-tests](https://github.com/idle-code/tempren/actions/workflows/run-tests.yml/badge.svg)
[![codecov](https://codecov.io/gh/idle-code/tempren/branch/develop/graph/badge.svg?token=1CR2PX6GYB)](https://codecov.io/gh/idle-code/tempren)
[![PyPI version](https://badge.fury.io/py/tempren.svg)](https://badge.fury.io/py/tempren)

`tempren` is a powerful batch file renamer that can generate filenames based on flexible template expressions.
It can create new or process existing filenames or sort files into directories based on their attributes (metadata).

**This project is currently in a Work-In-Progress stage so if you are looking for working solution... keep looking.**

## Features
- Template-based filename/path generation
- Configurable file selection (filtering)
- Metadata-based sorting


# Quickstart (5 minutes required)
People don't have to rename massive amounts of files very often and
learning new software just to solve the problem you are facing sporadically
might be daunting.

This quickstart is meant to introduce you to the `tempren` and give you
enough information to make sure it is up to the task you are facing.
You will need around 5 minutes total to work through it.

For more comprehensive documentation please refer to the [manual](MANUAL.md).

## Install
```console
$ pip install [--user] tempren
```

## Usage

**Note: When playing with tempren make sure to use `--dry-run` (`-d`) flag so that the actual files are not accidentally changed.**

Tempren have two main modes of operation: **name** and **path**.

In the **name** mode (default, enabled by `-n`, `--name` flag), the template is used for filename generation only.
This is useful if you want to operate on files specified on the command line or in a single directory.

With **path** mode (enabled by `-p`, `--path` flag), the template generates a whole path (relative to the input directory).
This way you can sort files into dynamically generated catalogues.

### Template syntax
Tag template consists of raw text interleaved with tag invocations.
Each tag invocation starts with `%` (percent) character followed by tag name, tag configuration (argument) list (enclosed in `()` parentheses) and - optionally -
tag context (enclosed in `{}` parentheses). Consider following template:
```tempren
File_%Count(start=100).%Lower(){%Ext()}
```

Above expression can be split into:
- Raw text `File_`
- `Count` tag configured with `start` parameter set to `100`
- Raw text `.`
- `Lower` tag (with empty configuration list) operating on context rendered from:
  - `Ext` tag

**Note: You can use `--list-tags` flag to print tag names provided by your `tempren` version.**

When used withing tempren:
```console
$ tempren -d "File_%Count(start=100).%Lower(){%Ext()}" test_directory/
```
One may expect results as:

| Input name   | Output name  |
|--------------|--------------|
| test.sh      | File_100.sh  |
| img1.jpg     | File_101.jpg |
| IMG_1414.jpg | File_102.jpg |
| document.pdf | File_102.pdf |


#### Tag configuration
#### Pipe list sugar
### Name mode
### Path mode
### Filtering
To select which files should be considered for processing one can use filtering predicate.

There are three types of a filtering expressions supported (by `-ft`, `--filter-type` option):
- `glob` (default) - filename globbing expression, eg: `*.mp3`, `IMG_????.jpg`
- `regex` - python-flavored regex, eg: `.*\.jpe?g`
- `template` - tag-template evaluated python expression, eg: `%Size() > 10*1024`

Sometimes it might be easier to specify filter for files which should **not** be included.
To negate/invert filtering expression you can use `-fi`, `--filter-invert` flag.

#### Glob filtering
#### Regex filtering
#### Template filtering
#### Case sensitiveness and filter inversion
TODO: **IMPLEMENT**

By default, `glob` and `regex` filtering expressions will match case-sensitive.
To allow case-insensitive matching use `-fc`, `--filter-case` flag.

`template` filter isn't affected by case-sensitivity flag - you will have to make use of `str.upper` or `str.lower` python methods to simulate that.

### Sorting

## Contribution
Minimal Python version supported is 3.7, so you should make sure that you have it installed on your system.
You can use `pyenv` for that:
```console
$ pyenv shell 3.7.10
```

After cloning repo you should install `poetry` as it is used for dependency resolution and packaging:
```console
$ pip install [--user] poetry
```

It is good to use separate virtualenv for development, `poetry` can spawn one:
```console
# Make sure that your `python --version` is at least 3.7 before this step
$ poetry shell
```

Now you can install required packages (specified in `pyproject.toml`) via:
```console
$ poetry install
```

Code conventions are enforced via [pre-commit](https://pre-commit.com/). It is listed in development depenencies so if you are able to run tests - you should have it installed too.
To get started you will still need to install git hooks:
```console
$ pre-commit install
```
Now every time you invoke `git commit` a series of cleanup scripts will run and modify your patchset.

### Testing
Tests are written with a help of [pytest](https://docs.pytest.org/en/latest/). Just enter repository root and run:
```console
$ pytest
```

`mypy` on the other hand takes care of static analysis - it can catch early type-related errors:
```console
$ mypy
```

### TODO: Tags development
