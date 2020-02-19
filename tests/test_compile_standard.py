#!/usr/bin/python3

from pathlib import Path

import pytest

import solcx
from solcx.exceptions import ContractsNotFound, SolcError


@pytest.fixture(autouse=True)
def setup(all_versions):
    pass


@pytest.fixture
def input_json():
    json = {
        "language": "Solidity",
        "sources": {},
        "settings": {"outputSelection": {"*": {"*": ["evm.bytecode.object"]}}},
    }
    yield json


def test_compile_standard(input_json, foo_source):
    input_json["sources"] = {"contracts/Foo.sol": {"content": foo_source}}
    result = solcx.compile_standard(input_json)

    _compile_assertions(result, "Foo")


def test_compile_standard_invalid_source(input_json, invalid_source):
    input_json["sources"] = {"contracts/Foo.sol": {"content": invalid_source}}
    with pytest.raises(SolcError):
        solcx.compile_standard(input_json)


def test_compile_standard_with_dependency(input_json, foo_source, bar_source):
    input_json["sources"] = {
        "contracts/Foo.sol": {"content": foo_source},
        "contracts/Bar.sol": {"content": bar_source},
    }
    result = solcx.compile_standard(input_json)

    _compile_assertions(result, "Foo", "Bar")


def test_compile_standard_with_file_paths(input_json, foo_path):
    input_json["sources"] = {"contracts/Foo.sol": {"urls": [foo_path]}}
    result = solcx.compile_standard(input_json, allow_paths=Path(foo_path).parent.as_posix())

    _compile_assertions(result, "Foo")


def test_compile_standard_empty():
    with pytest.raises(ContractsNotFound):
        solcx.compile_standard({"language": "Solidity", "sources": {}})


def _compile_assertions(output_json, *contract_names):
    assert isinstance(output_json, dict)
    assert "contracts" in output_json
    contracts = output_json["contracts"]
    for key in contract_names:
        assert int(contracts[f"contracts/{key}.sol"][key]["evm"]["bytecode"]["object"], 16)
