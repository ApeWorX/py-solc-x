#!/usr/bin/python3

from pathlib import Path

import pytest

import solcx
from solcx.exceptions import ContractsNotFound
from solcx.main import ALL_OUTPUT_VALUES

# interfaces and compact-format do not return anything
combined_json_values = (
    "abi",
    "asm",
    "ast",
    "bin",
    "bin-runtime",
    "devdoc",
    "hashes",
    "metadata",
    "opcodes",
    "srcmap",
    "srcmap-runtime",
    "userdoc",
)


@pytest.fixture(autouse=True)
def setup(all_versions):
    pass


def test_compile_source(foo_source):
    output = solcx.compile_source(foo_source)
    _compile_assertions(output, "<stdin>:Foo")
    output = solcx.compile_source(foo_source, optimize=True)
    _compile_assertions(output, "<stdin>:Foo")


def test_compile_source_empty():
    with pytest.raises(ContractsNotFound):
        solcx.compile_source("  ")
    solcx.compile_source("  ", allow_empty=True)


@pytest.mark.parametrize("key", combined_json_values)
def test_compile_source_output_types(foo_source, key):
    if key == "hashes" and str(solcx.get_solc_version().truncate()) == "0.4.11":
        return
    output = solcx.compile_source(foo_source, output_values=[key])
    assert key in output["<stdin>:Foo"]


def test_compile_files(foo_path):
    output = solcx.compile_files([foo_path])
    _compile_assertions(output, f"{foo_path}:Foo")
    output = solcx.compile_files([foo_path], optimize=True)
    _compile_assertions(output, f"{foo_path}:Foo")


def test_compile_files_empty():
    with pytest.raises(ContractsNotFound):
        solcx.compile_files([])
    solcx.compile_files([], allow_empty=True)


@pytest.mark.parametrize("key", combined_json_values)
def test_compile_files_output_types(foo_path, key):
    if key == "hashes" and str(solcx.get_solc_version().truncate()) == "0.4.11":
        return
    output = solcx.compile_files([foo_path], output_values=[key])
    assert key in output[f"{foo_path}:Foo"]


def test_compile_files_import_remapping(foo_path, bar_path):
    path = Path(bar_path).parent.as_posix()
    output = solcx.compile_files([bar_path], import_remappings=[f"contracts={path}"])
    assert output
    assert f"{bar_path}:Bar" in output


def _compile_assertions(output, key):
    assert output
    assert key in output
    for value in ALL_OUTPUT_VALUES:
        if value == "clone-bin" and solcx.get_solc_version().minor >= 5:
            assert value not in output[key]
        else:
            assert value in output[key]
