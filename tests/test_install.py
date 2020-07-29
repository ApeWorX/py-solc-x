#!/usr/bin/python3

import sys

import pytest

import solcx
from solcx.exceptions import DownloadError, SolcNotInstalled


@pytest.fixture(autouse=True)
def isolation():
    p = sys.platform
    v = solcx.install._default_solc_binary
    yield
    sys.platform = p
    solcx.install._default_solc_binary = v


def test_not_installed():
    solcx.install.get_executable()
    with pytest.raises(ValueError):
        solcx.install.get_executable("v0.4.0")
    solcx.install._default_solc_binary = None
    with pytest.raises(SolcNotInstalled):
        solcx.install.get_executable()


def test_unsupported_version():
    solcx.install._convert_and_validate_version("0.4.11")
    with pytest.raises(ValueError):
        solcx.install._convert_and_validate_version("0.4.10")


def test_unknown_platform():
    sys.platform = "potatoOS"
    with pytest.raises(OSError):
        solcx.install_solc("0.5.0")


def test_install_unknown_version():
    with pytest.raises(DownloadError):
        solcx.install_solc("0.4.99")


@pytest.mark.skipif("'--no-install' in sys.argv")
def test_progress_bar(nosolc):
    solcx.install_solc("0.6.9", show_progress=True)


def test_environment_var_path(monkeypatch, tmp_path):
    install_folder = solcx.get_solcx_install_folder()
    monkeypatch.setenv("SOLCX_BINARY_PATH", tmp_path.as_posix())
    assert solcx.get_solcx_install_folder() != install_folder

    monkeypatch.undo()
    assert solcx.get_solcx_install_folder() == install_folder


def test_environment_var_versions(monkeypatch, tmp_path):
    versions = solcx.get_installed_solc_versions()
    monkeypatch.setenv("SOLCX_BINARY_PATH", tmp_path.as_posix())
    assert solcx.get_installed_solc_versions() != versions

    monkeypatch.undo()
    assert solcx.get_installed_solc_versions() == versions


@pytest.mark.skipif("'--no-install' in sys.argv")
def test_environment_var_install(monkeypatch, tmp_path):
    assert not tmp_path.joinpath("solc-v0.6.9").exists()

    monkeypatch.setenv("SOLCX_BINARY_PATH", tmp_path.as_posix())

    solcx.install_solc("0.6.9")
    assert tmp_path.joinpath("solc-v0.6.9").exists()
