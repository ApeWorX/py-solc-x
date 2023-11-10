import sys
import warnings

import pytest

import solcx
from solcx.exceptions import SolcInstallationError, UnexpectedVersionError, UnexpectedVersionWarning


def test_validate_installation(mocker, install_mock, solc_binary, install_path):
    version = solcx.wrapper.get_solc_version(solc_binary)
    version_str_patch = mocker.patch("solcx.wrapper.get_version_str_from_solc_binary")
    version_str_patch.return_value = f"{version}"

    # This should not warn!
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        solcx.install_solc()

    assert install_path.exists()


def test_validate_installation_wrong_version(mocker, install_mock, install_path):
    patch = mocker.patch("solcx.wrapper.get_version_str_from_solc_binary")
    patch.return_value = "0.0.0"

    with pytest.raises(UnexpectedVersionError):
        solcx.install_solc()

    assert not install_path.exists()


def test_validate_installation_nightly(mocker, install_mock, solc_binary, install_path):
    version = solcx.wrapper.get_solc_version(solc_binary)
    version_str_patch = mocker.patch("solcx.wrapper.get_version_str_from_solc_binary")
    version_str_patch.return_value = f"{version}-nightly"

    with pytest.warns(UnexpectedVersionWarning):
        solcx.install_solc()

    assert install_path.exists()


def test_validate_installation_fails(monkeypatch, solc_binary, install_path):
    def _mock(*args, **kwargs):
        if sys.platform == "win32":
            install_path.mkdir()
            with install_path.joinpath("solc.exe").open("w") as fp:
                fp.write("blahblah")
        else:
            with install_path.open("w") as fp:
                fp.write("blahblah")

    monkeypatch.setattr("solcx.install._install_solc_unix", _mock)
    monkeypatch.setattr("solcx.install._install_solc_windows", _mock)

    with pytest.raises(SolcInstallationError):
        solcx.install_solc()

    assert not install_path.exists()
