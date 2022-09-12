## Contributing
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
TODO: Establish convention for error reporting in `process` and `configure` methods (`if`'s vs `assert`)
