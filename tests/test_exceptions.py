import inspect

import pytest

import tempren.cli
import tempren.exceptions
import tempren.template.compiler
import tempren.template.exceptions
import tempren.template.registry
from tempren.exceptions import (
    DestinationAlreadyExistsError,
    DestinationError,
    FileMetadataError,
    TemprenError,
)
from tempren.template.exceptions import InvalidFilenameError


def _exception_classes(module):
    return [
        cls
        for _, cls in inspect.getmembers(module, inspect.isclass)
        if issubclass(cls, BaseException) and cls.__module__ == module.__name__
    ]


@pytest.mark.parametrize(
    "module",
    [
        tempren.exceptions,
        tempren.template.exceptions,
        tempren.template.compiler,
        tempren.template.registry,
        tempren.cli,
    ],
)
def test_all_exceptions_derive_from_tempren_error(module):
    classes = _exception_classes(module)

    assert classes
    for cls in classes:
        assert issubclass(cls, TemprenError), cls


def test_destination_already_exists_is_file_exists_error():
    error = DestinationAlreadyExistsError("src", "dst")

    assert isinstance(error, FileExistsError)
    assert isinstance(error, DestinationError)
    assert (
        str(error) == "Could not rename 'src' as destination path 'dst' already exists"
    )


def test_invalid_filename_is_destination_error():
    assert issubclass(InvalidFilenameError, DestinationError)


def test_tag_extraction_errors_are_file_metadata_errors():
    assert issubclass(tempren.exceptions.FileNotSupportedError, FileMetadataError)
    assert issubclass(tempren.exceptions.ExecutionTimeoutError, FileMetadataError)
