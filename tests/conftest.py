from base64 import b64encode
import os
import pytest
import sys

import solcx

TEST_CONTRACT = '''pragma solidity >=0.4.11 <0.6.0;

contract Foo {
    function return13() public returns (uint) {
        return 13;
    }
}
'''

if sys.platform == "darwin":
    VERSIONS = solcx.get_installed_solc_versions()
else:
    auth = b64encode(os.environ['GITAUTH'].encode()).decode('ascii')
    headers = {'Authorization': f"Basic {auth}"}
    VERSIONS = solcx.get_available_solc_versions(headers=headers)


# auto-parametrize the all_versions fixture with all target solc versions
def pytest_generate_tests(metafunc):
    if 'all_versions' in metafunc.fixturenames:
        metafunc.parametrize('all_versions', VERSIONS, indirect=True)


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
        request.applymarker('skip')


@pytest.fixture()
def contract_path(tmp_path):
    source = tmp_path.joinpath('test.sol')
    with source.open('w') as fp:
        fp.write(TEST_CONTRACT)
    return str(source)


@pytest.fixture()
def contract_source():
    yield TEST_CONTRACT
