#!/usr/bin/python3

import pytest
from packaging.version import Version
from requests import ConnectionError

import solcx

_installed: dict = {}
VERSIONS = []


def pytest_addoption(parser):
    parser.addoption(
        "--no-install",
        action="store_true",
        help="Only run solcx tests against already installed solc versions",
    )
    parser.addoption(
        "--solc-versions",
        action="store",
        help="Only run tests against a specific version(s) of solc",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "min_solc: minimum version of solc to run test against")


def pytest_collection(session):
    global VERSIONS
    if session.config.getoption("--solc-versions"):
        VERSIONS = [Version(i) for i in session.config.getoption("--solc-versions").split(",")]
    elif session.config.getoption("--no-install"):
        VERSIONS = solcx.get_installed_solc_versions()
    else:
        try:
            VERSIONS = solcx.get_installable_solc_versions()
        except ConnectionError:
            raise pytest.UsageError(
                "ConnectionError while attempting to get solc versions.\n"
                "Use the --no-install flag to only run tests against already installed versions."
            )
        for version in VERSIONS:
            solcx.install_solc(version)


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


@pytest.fixture(scope="session")
def foo_source():
    yield """pragma solidity >=0.4.1;

contract Foo {
    function return13() public returns (uint a) {
        return 13;
    }
}
"""


@pytest.fixture(scope="session")
def bar_source():
    yield """
pragma solidity >=0.4.1;

import "../contracts/Foo.sol";

contract Bar is Foo {
    function getFunky() public returns (bytes4) {
        return 0x420Faded;
    }
}"""


@pytest.fixture(scope="session")
def baz_source():
    yield """
pragma solidity >=0.4.1;

import "../other/Bar.sol";

contract Baz is Bar {
    function doStuff() public returns (uint a) {
        return 31337;
    }
}"""


@pytest.fixture()
def invalid_source():
    yield """pragma solidity >=0.4.1;
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
