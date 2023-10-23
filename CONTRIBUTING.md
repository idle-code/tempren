<!-- TOC -->
* [Development environment setup](#development-environment-setup)
* [Testing](#testing)
  * [Directory layout](#directory-layout)
* [Tags development](#tags-development)
  * [Renaming pipeline](#renaming-pipeline)
<!-- TOC -->

# Development environment setup
Minimal Python version supported is 3.8, so you should make sure that you have it installed on your system.\
Alternatively, you can use [pyenv](https://github.com/pyenv/pyenv) for runtime management as follows:
```commandline
# Install Python 3.8:
pyenv install 3.8.16
# Activate installed python for the current shell session:
pyenv shell 3.8.16
```

After cloning the repository you should install [poetry](https://python-poetry.org/) - it is used for dependency resolution and packaging:
```commandline
pip install [--user] poetry
```

In the cloned `tempren` directory, you can spawn new virtualenv as its good idea to use separate one for the development. `poetry` can be used here to create one and activate it with one `poetry shell` command:
```commandline
# Make sure that your `python --version` is at least 3.8 before this step:
python --version
poetry shell
```

Now you can install required packages (specified in `pyproject.toml`/`poetry.lock`) via:
```commandline
poetry install [--no-root] --all-extras
```
This will install all development dependencies (mypy, pytest, pre-commit) and video tags as well.\
The `--no-root` option can be used to omit installation of the `tempren` itself if you are not using virtualenvs and do not want to pollute your systems' packages.

> Note: When using `--all-extras` option you will also need to install additional dependencies as stated in the [manual](MANUAL.md#additional-dependencies). If those are not met, you will get errors when running the test suite.

Code conventions are enforced via [pre-commit](https://pre-commit.com/) and to get started you will still need to install its git hooks:
```commandline
pre-commit install
```
With this, every time you invoke `git commit` a series of cleanup scripts will run and modify your patchset to the state suitable for the commitment into the repository.

> Note: In all other subsequent shell sessions (after you close your terminal window), the only thing you will need to do to get back to the development is to invoke `poetry shell` in the project directory to activate tempren's environment.

# Testing
We try to keep the high quality of the project by using extensive test suite.

Tests are written with the help of [pytest](https://docs.pytest.org/en/latest/) and can be run by invoking the following command in the project root directory:
```commandline
pytest
```
Due to dynamic nature of the Python, [mypy](https://github.com/python/mypy) is used to take care of static analysis - it can catch early type-related errors. Just invoke the following command in the project root directory:
```commandline
mypy
```

If those two command succeed, you are ready to start the development.

> Note: If you want to create Pull Request to the main repository, both `pytest` and `mypy` commands have to succeed as they are invoked by the CI pipeline.

## Directory layout
Test modules hierarchy (`tests` directory) mirrors the source code layout (under `tempren` directory). The tests themselves are divided into two categories: unit and end-to-end.

Ent-to-end tests cover mostly CLI interface, error reporting and features that are hard to test using unit tests. Those tests are placed under `tests/e2e` directory.
They are basically black-box tests where `tempren` is executed as an external process and test validates its output/filesystem state.\
The overhead associated with process execution makes end-to-end tests take longer, so unit tests should be preferred whenever possible (especially for tags development).

Unit tests cover everything else - from parsing, through filesystem access modules to tags themselves.
This kind of test should execute quickly, so they can be run continuously in the background during development process.


# Tags development
To create a new tag, you should choose its name and category.
Then you can create a Python class which will be used to instantiate tags in the _tag templates_.

Automatic tag discovery looks for tag classes in Python modules under `tempren/tags` directory and creates factories for them.\
Module (file) name is used as the _tag category_, while class name (without `Tag` suffix) is used as a tag name.
Tag classes should have `Tag` suffix and inherit from the `tempren.primitives.Tag` class to be discoverable.

For example: `class MyTag(Tag)` defined in `tempren/tags/sample.py` file will introduce tag `My` under `Sample` category. Which can be used in the template as `%Sample.My()`.

`tempren.primitives.Tag` superclass outlines main tag elements:
- property `require_context` indicates if the tag accepts, require or forbids context passing
- method `configure` is used to receive arguments passed in the tag argument list (in the _tag template_) to set up the tag instance before renaming can begin
- method `process` is invoked for each file considered for renaming in the renaming pipeline

Additionally, tag class docstring (e.g. `MyTag.__doc__`) is used as built-in documentation presented to the user (when `--list-tags` or `--help My` flags are used).
`configure` method docstring (e.g. `MyTag.configure.__doc__`) is also used to generate tag prototype documentation (accessible via `--help My` flag).

## Renaming pipeline
At the startup, command line arguments are gathered to the `RuntimeConfiguration` instance.
This is DTO is used in pipeline building procedure which consists of:
- Tag (factories) discovery
- Preparations of pipeline stages (which implementations will be used for specified stage)
- Tag template compilation (this includes main and filtering/sorting templates if those were specified)

When pipeline has been created, it can be used in the renaming process.

Renaming process consist of few steps which are contained in the `Pipeline` class:
- File gathering
- (optional) Filtering
- (optional) Sorting
- Name/Path generation
- Renaming

`tempren` uses paths passed in the command line to find the files to be renamed.
If a directory path has been passed, the `FilesystemGatherer` will be used to traverse its contents.
In the case of file paths - simple `ExplicitFileGatherer` will be used.

The filtering phase is executed during the file discovery process for efficiency - we don't need to store paths that won't be even considered for renaming.

Sorting stage is optional and executed only if the sorting expression has been specified.

Name/Path generation works basically the same.
The only difference between those modes is that in the case of name generation, an error is reported if a path separator is detected in the generated output.

Actual renaming depends on the mode which determines what filesystem operations will be used.
For the **path** mode, `move` filesystem operation is used, while **name** mode, utilizes the `rename` operation.
If `--dry-run`/`-d` flag has been specified, `DryRunRenamer` is selected and no renaming is performed. All other stages are unaffected by this flag.
