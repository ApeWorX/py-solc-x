#!/usr/bin/python3

from pathlib import Path
import pytest

import solcx
from solcx.exceptions import ContractsNotFound


@pytest.fixture(autouse=True)
def setup(all_versions):
    pass


def test_compile_source(foo_source):
    output = solcx.compile_source(foo_source, optimize=True)
    _compile_assertions(output, "<stdin>:Foo")


def test_compile_source_empty():
    with pytest.raises(ContractsNotFound):
        solcx.compile_source("  ")


def test_compile_files(foo_path):
    output = solcx.compile_files([foo_path])
    _compile_assertions(output, f"{foo_path}:Foo")


def test_import_remapping(foo_path, bar_path):
    path = Path(bar_path).parent.as_posix()
    output = solcx.compile_files([bar_path], import_remappings=[f"contracts={path}"])
    assert output
    assert f'{bar_path}:Bar' in output


def test_compile_files_empty():
    with pytest.raises(ContractsNotFound):
        solcx.compile_files([])


def _compile_assertions(output, key):
    assert output
    assert key in output
    assert 'bin' in output[key]
    assert 'bin-runtime' in output[key]
