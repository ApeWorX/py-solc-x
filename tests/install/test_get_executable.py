import pytest

import solcx
from solcx.exceptions import SolcNotInstalled, UnsupportedVersionError


def test_get_executable():
    assert solcx.install.get_executable() == solcx.install._default_solc_binary


def test_no_default_set(nosolc):
    with pytest.raises(SolcNotInstalled):
        solcx.install.get_executable()


def test_unsupported_version():
    with pytest.raises(UnsupportedVersionError):
        solcx.install.get_executable("0.4.0")


def test_version_not_installed():
    with pytest.raises(SolcNotInstalled):
        solcx.install.get_executable("999.999.999")
