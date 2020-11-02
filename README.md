# [WIP] Tempren - template-based batch file renaming utility
[![Build Status](https://travis-ci.org/idle-code/tempren.svg?branch=develop)](https://travis-ci.org/idle-code/tempren)
[![codecov](https://codecov.io/gh/idle-code/tempren/branch/develop/graph/badge.svg?token=1CR2PX6GYB)](https://codecov.io/gh/idle-code/tempren)

**This project is currently in a Work-In-Progress stage so if you are looking for working solution... keep looking.**

TODO: Summary

## Features
- [ ] Batch file renaming
- [ ] Metadata extraction
  - [ ] ID3 tags
  - [ ] EXIF
- [x] Template language for specifying name generation patterns
- [ ] Metadata-based filtering
- [ ] Metadata-based sorting
- [ ] Can operate on whole path (to move files and create directories)
- [ ] Plugins infrastructure

## Install
```console
$ pip install [--user] poetry
$ poetry install
```

## TODO: Usage

## Contribution
Code convetions are enforced via [pre-commit](https://pre-commit.com/). It is listed in development depenencies so if you are able to run tests - you should have it installed too.
To get started you will still need to install git hooks via:
```console
$ pre-commit install
```
Now every time you invoke `git commit` a series of cleanup scripts will run and modify your patchset.

### TODO: Testing
Tests are written with a help of [pytest](https://docs.pytest.org/en/latest/). Just enter repository root and run:
```console
$ pytest
```

### TODO: Plugin development
