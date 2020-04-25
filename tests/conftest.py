#!/usr/bin/python3

import shutil

import pytest
from requests import ConnectionError

import solcx


def pytest_addoption(parser):
    parser.addoption(
        "--no-install",
        action="store_true",
        help="Only run solcx tests against already installed solc versions",
    )


def pytest_configure(config):
    global VERSIONS
    if config.getoption("--no-install"):
        VERSIONS = solcx.get_installed_solc_versions()
        return
    try:
        VERSIONS = solcx.get_available_solc_versions()
    except ConnectionError:
        raise pytest.UsageError(
            "ConnectionError while attempting to get solc versions.\n"
            "Use the --no-install flag to only run tests against already installed versions."
        )


# auto-parametrize the all_versions fixture with all target solc versions
def pytest_generate_tests(metafunc):
    if "all_versions" in metafunc.fixturenames:
        metafunc.parametrize("all_versions", VERSIONS, indirect=True)


# * runs a test against all target solc versions
# * the first test using this fixture attempts to install every version
# * if an install fails all subsequent tests on that version are skipped
_installed = {}


@pytest.fixture()
def all_versions(request):
    version = request.param
    if version not in _installed:
        try:
            solcx.install_solc(version)
            _installed[version] = True
        except Exception:
            _installed[version] = False
            pytest.fail(f"Unable to install solc {version}")
    if _installed[version]:
        solcx.set_solc_version(version)
    else:
        request.applymarker("skip")


# run tests with no installed versions of solc
@pytest.fixture
def nosolc():
    path = solcx.install.get_solc_folder()
    temp_path = path.parent.joinpath(".temp")
    path.rename(temp_path)
    yield
    if path.exists():
        shutil.rmtree(path)
    temp_path.rename(path)


@pytest.fixture()
def foo_source():
    yield """pragma solidity >=0.4.11;

contract Foo {
    function return13() public returns (uint a) {
        return 13;
    }
}
"""


@pytest.fixture()
def bar_source():
    yield """
pragma solidity >=0.4.11;

import "contracts/Foo.sol";

contract Bar is Foo {
    function getFunky() public returns (bytes4) {
        return 0x420Faded;
    }
}"""


@pytest.fixture()
def invalid_source():
    yield """pragma solidity >=0.4.11;
contract Foo {"""


@pytest.fixture()
def foo_path(tmp_path, foo_source):
    source = tmp_path.joinpath("Foo.sol")
    with source.open("w") as fp:
        fp.write(foo_source)
    return source.as_posix()


@pytest.fixture()
def bar_path(tmp_path, bar_source):
    source = tmp_path.joinpath("Bar.sol")
    with source.open("w") as fp:
        fp.write(bar_source)
    return source.as_posix()
