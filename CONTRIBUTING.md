## Development environment setup
Minimal Python version supported is 3.7, so you should make sure that you have it installed on your system.
You can use `pyenv` for that:
```console
$ pyenv shell 3.7.10
```

After cloning the repository you should install `poetry` as it is used for dependency resolution and packaging:
```console
$ pip install [--user] poetry
```

It is a good idea to use separate virtualenv for development, `poetry` can spawn one with following command:
```console
# Make sure that your `python --version` is at least 3.7 before this step
$ poetry shell
```

Now you can install required packages (specified in `pyproject.toml`) via:
```console
$ poetry install
```

Code conventions are enforced via [pre-commit](https://pre-commit.com/) (which is installed as part of dev dependencies).
To get started you will still need to install its git hooks:
```console
$ pre-commit install
```
With this, every time you invoke `git commit` a series of cleanup scripts will run and modify your patchset.

Now you have the development environment ready - we can go straight to the code!

Note: most of the commands above need to be executed just once.
When you close your terminal window, you will just need to run `poetry shell` to start working again.

### Testing
Tests are written with a help of [pytest](https://docs.pytest.org/en/latest/). Just enter repository root and run:
```console
$ pytest
```

`mypy` on the other hand takes care of static analysis - it can catch early type-related errors:
```console
$ mypy
```

Test modules hierarchy (`tests` directory) mirrors source code layout (under `tempren` directory).

Tests are divided into two categories: unit and functional.

Functional tests cover mostly CLI interface and error reporting. Those tests are placed in the `tests/test_cli.py` file.
They are basically black-box tests where `tempren` is executed as an external process and test validates its output/filesystem state.
The overhead associated with process execution makes functional tests take longer, so unit tests should be preferred.

Unit tests cover everything else - from parsing, through filesystem access modules to tags themselves.
This kind of test should execute quickly (so in the future they can be run continuously in the background).


### Tags development
To create a new tag, you should choose its name and category.
Then you can create a Python class which will be used to instantiate tags in the _tag templates_.

Automatic tag discovery looks for tag classes in Python modules under `tempren/tags` directory.
Module (file) name is used as the _tag category_.
Each tag (class) name should have `Tag` suffix and inherit from the `tempren.template.tree_elements.Tag` superclass.
For example: `class MyTag(Tag)` defined in `tempren/tags/sample.py` file will introduce `My` tag under `Sample` category.

`tempren.template.tree_elements.Tag` superclass outlines main tag elements:
- `require_context` property which indicates if the tag accepts/requires/forbids context passing
- `configure` method used to receive arguments passed in the argument list (in the _tag template_) to set up the tag instance before renaming can begin
- `process` method invoked for each file considered for renaming

Tag class docstring (e.g. `MyTag.__doc__`) is used as built-in documentation presented to the user (when `--list-tags` or `--help My` flags are used).
`configure` method docstring (e.g. `MyTag.configure.__doc__`) is also used for detailed configuration documentation (accessible via `--help My` flag).
