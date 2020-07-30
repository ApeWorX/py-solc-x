#!/usr/bin/python3

import json

import pytest

import solcx
from solcx.exceptions import ContractsNotFound, SolcError

# these values should work for all compatible solc versions
combined_json_values = (
    "abi",
    "asm",
    "ast",
    "bin",
    "bin-runtime",
    "devdoc",
    "metadata",
    "opcodes",
    "srcmap",
    "srcmap-runtime",
    "userdoc",
)


@pytest.fixture(autouse=True)
def setup(all_versions):
    pass


def test_compile_single_file(foo_path):
    output = solcx.compile_files([foo_path])
    assert f"{foo_path.as_posix()}:Foo" in output
    for value in combined_json_values:
        assert value in output[f"{foo_path.as_posix()}:Foo"]


def test_compile_multiple_files(foo_path, bar_path, baz_path):
    output = solcx.compile_files([foo_path, bar_path, baz_path])

    assert set(output) == {
        f"{foo_path.as_posix()}:Foo",
        f"{bar_path.as_posix()}:Bar",
        f"{baz_path.as_posix()}:Baz",
    }


def test_compile_multiple_files_fails_bad_path(baz_path):
    with pytest.raises(SolcError):
        solcx.compile_files([baz_path])


def test_import_remappings(foo_path, bar_path, baz_path):
    import_remappings = {"contracts": foo_path.parent, "other": bar_path.parent}
    output = solcx.compile_files([baz_path], import_remappings=import_remappings)

    assert set(output) == {
        f"{foo_path.as_posix()}:Foo",
        f"{bar_path.as_posix()}:Bar",
        f"{baz_path.as_posix()}:Baz",
    }


def test_allow_paths(foo_path, bar_path, baz_path):
    output = solcx.compile_files([baz_path], allow_paths=[foo_path.parent.parent])

    assert set(output) == {
        f"{foo_path.as_posix()}:Foo",
        f"{bar_path.as_posix()}:Bar",
        f"{baz_path.as_posix()}:Baz",
    }


def test_compile_files_empty(empty_path):
    with pytest.raises(ContractsNotFound):
        solcx.compile_files([empty_path])


def test_compile_files_allow_empty(empty_path):
    assert solcx.compile_files([empty_path], allow_empty=True) == {}


@pytest.mark.parametrize("key", combined_json_values)
def test_compile_files_output_types(foo_path, key):
    output = solcx.compile_files([foo_path], output_values=[key])
    assert list(output[f"{foo_path.as_posix()}:Foo"]) == [key]


def test_compile_source_output_dir(tmp_path, foo_path, bar_path):
    solcx.compile_files([foo_path, bar_path], output_dir=tmp_path)
    output_path = tmp_path.joinpath("combined.json")

    with output_path.open() as fp:
        output = json.load(fp)["contracts"]

    assert f"{foo_path.as_posix()}:Foo" in output
    assert f"{bar_path.as_posix()}:Bar" in output
