import pytest

import solcx


@pytest.fixture(autouse=True)
def setup(all_versions):
    pass


def test_compile_files(contract_path):
    solcx.compile_files([contract_path])


def test_compile_source(contract_source):
    solcx.compile_source(contract_source)
