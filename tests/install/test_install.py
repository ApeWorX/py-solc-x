import warnings

import pytest

import solcx
from solcx.exceptions import SolcInstallationError


@pytest.mark.skipif("'--no-install' in sys.argv")
def test_install_latest():
    version = solcx.get_installable_solc_versions()[0]
    assert solcx.install_solc("latest") == version


def test_unknown_platform(monkeypatch):
    monkeypatch.setattr("sys.platform", "potatoOS")
    with pytest.raises(OSError):
        solcx.install_solc()


def test_install_unknown_version():
    with pytest.raises(SolcInstallationError):
        solcx.install_solc("0.4.99")


@pytest.mark.skipif("'--no-install' in sys.argv")
def test_progress_bar(nosolc):
    # There should be no warnings!
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert solcx.install_solc("0.6.9", show_progress=True).base_version == "0.6.9"


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
