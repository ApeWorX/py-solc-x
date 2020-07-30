#!/usr/bin/python3

import pytest
from requests import ConnectionError
from semantic_version import Version

import solcx

_installed = {}


def pytest_addoption(parser):
    parser.addoption(
        "--no-install",
        action="store_true",
        help="Only run solcx tests against already installed solc versions",
    )


def pytest_configure(config):
    global VERSIONS
    config.addinivalue_line("markers", "min_solc: minimum version of solc to run test against")

    if config.getoption("--no-install"):
        VERSIONS = solcx.get_installed_solc_versions()
        return

    try:
        VERSIONS = solcx.get_available_solc_versions()
        for version in VERSIONS:
            solcx.install_solc(version)
    except ConnectionError:
        raise pytest.UsageError(
            "ConnectionError while attempting to get solc versions.\n"
            "Use the --no-install flag to only run tests against already installed versions."
        )


# auto-parametrize the all_versions fixture with all target solc versions
def pytest_generate_tests(metafunc):
    if "all_versions" in metafunc.fixturenames:
        versions = VERSIONS.copy()
        for marker in metafunc.definition.iter_markers(name="min_solc"):
            versions = [i for i in versions if i >= Version(marker.args[0])]
        metafunc.parametrize("all_versions", versions, indirect=True)


@pytest.fixture
def all_versions(request):
    """
    Run a test against all solc versions.
    """
    version = request.param
    solcx.set_solc_version(version)
    return version


@pytest.fixture
def nosolc(tmp_path, monkeypatch):
    """
    Monkeypatch the install folder, so tests run with no versions of solc installed.
    """
    monkeypatch.setattr("solcx.install.get_solcx_install_folder", lambda *args: tmp_path)


@pytest.fixture(scope="session")
def foo_source():
    yield """pragma solidity >=0.4.11;

contract Foo {
    function return13() public returns (uint a) {
        return 13;
    }
}
"""


@pytest.fixture(scope="session")
def bar_source():
    yield """
pragma solidity >=0.4.11;

import "../contracts/Foo.sol";

contract Bar is Foo {
    function getFunky() public returns (bytes4) {
        return 0x420Faded;
    }
}"""


@pytest.fixture(scope="session")
def baz_source():
    yield """
pragma solidity >=0.4.11;

import "../other/Bar.sol";

contract Baz is Bar {
    function doStuff() public returns (uint a) {
        return 31337;
    }
}"""


@pytest.fixture()
def invalid_source():
    yield """pragma solidity >=0.4.11;
contract Foo {"""


@pytest.fixture(scope="session")
def foo_path(tmp_path_factory, foo_source):
    source = tmp_path_factory.mktemp("contracts", False).joinpath("Foo.sol")
    with source.open("w") as fp:
        fp.write(foo_source)
    return source


@pytest.fixture(scope="session")
def bar_path(tmp_path_factory, bar_source):
    source = tmp_path_factory.mktemp("other", False).joinpath("Bar.sol")
    with source.open("w") as fp:
        fp.write(bar_source)
    return source


@pytest.fixture(scope="session")
def baz_path(tmp_path_factory, baz_source):
    source = tmp_path_factory.mktemp("baz", False).joinpath("Baz.sol")
    with source.open("w") as fp:
        fp.write(baz_source)
    return source
