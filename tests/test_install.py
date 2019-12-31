#!/usr/bin/python3

import pytest
import sys

import solcx
from solcx.exceptions import SolcNotInstalled


@pytest.fixture(autouse=True)
def isolation():
    p = sys.platform
    v = solcx.install.solc_version
    yield
    sys.platform = p
    solcx.install.solc_version = v


def test_not_installed():
    solcx.install.get_executable()
    with pytest.raises(SolcNotInstalled):
        solcx.install.get_executable('v0.4.0')
    solcx.install.solc_version = None
    with pytest.raises(SolcNotInstalled):
        solcx.install.get_executable()


def test_unsupported_version():
    solcx.install._check_version('0.4.11')
    with pytest.raises(ValueError):
        solcx.install._check_version('0.4.10')


def test_unknown_platform():
    sys.platform = "potatoOS"
    with pytest.raises(KeyError):
        solcx.install_solc('0.5.0')


@pytest.mark.skipif("sys.platform == 'win32'")
def test_install_osx():
    sys.platform = "darwin"
    with pytest.raises(ValueError):
        solcx.install_solc('0.4.25')
    solcx.install_solc('0.4.25', allow_osx=True)
    solcx.install_solc('0.5.4')


def test_progress_bar(nosolc):
    solcx.install_solc('0.6.0', show_progress=True)
