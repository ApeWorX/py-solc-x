import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from packaging.version import Version

import solcx
from solcx.install import _download_solc


@pytest.fixture(scope="session")
def solc_binary():
    """
    Yields the path to the most recent solc binary.
    """
    version = solcx.get_installed_solc_versions()[0]
    yield solcx.install.get_executable(version)


@pytest.fixture
def nosolc(tmp_path, mocker):
    """
    Monkeypatch the install folder, so tests run with no versions of solc installed.

    Yields the temporary install folder.
    """
    install_patch = mocker.patch("solcx.install.get_solcx_install_folder")
    install_patch.return_value = tmp_path

    bin_patch = mocker.patch("solcx.install.get_default_solc_binary")
    bin_patch.return_value = None

    yield tmp_path


@pytest.fixture
def install_path(solc_binary, nosolc):
    """
    Yields the expected install path when using `install_mock`.
    """
    if sys.platform == "win32":
        yield nosolc.joinpath(solc_binary.parent.name)
    else:
        yield nosolc.joinpath(solc_binary.name)


@pytest.fixture
def install_mock(mocker, install_path, solc_binary):
    """
    Monkeypatches the install process by copying `solc_binary` to `install_path`.
    """

    def _mock(*args, **kwargs):
        if sys.platform == "win32":
            shutil.copytree(solc_binary.parent, install_path)
        else:
            shutil.copy(solc_binary, install_path)

    install_patch = mocker.patch("solcx.install._install_solc_unix")
    install_patch.side_effect = _mock

    windows_patch = mocker.patch("solcx.install._install_solc_windows")
    windows_patch.side_effect = _mock


class CompileMock:
    tarfile = None

    def __init__(self, solc_binary):
        self.solc_binary = solc_binary
        self.raise_cmd = None

    def __call__(self, cmd, **kwargs):
        if cmd[0] == self.raise_cmd:
            raise subprocess.CalledProcessError(1, cmd)
        if cmd == ["make"]:
            install_folder = Path(os.getcwd()).joinpath("solc")
            install_folder.mkdir()
            shutil.copy(self.solc_binary, install_folder.joinpath("solc"))

    def raise_on(self, cmd):
        self.raise_cmd = cmd

    @classmethod
    def download(cls, url, show_progress):
        if not cls.tarfile:
            cls.tarfile = _download_solc(url, show_progress)

        return cls.tarfile


@pytest.fixture
def compile_mock(monkeypatch, nosolc, solc_binary):
    """
    Monkeypatches `compile_solc`.

    * The first use downloads a tarfile, which is then returned for all subsequent uses
    * The call to `make` copies `solc_binary` to the expected location
    * `compile_make.raise_on` tells the mock to raise `CalledProcessError` on a specific command
    """
    mock = CompileMock(solc_binary)
    monkeypatch.setattr("subprocess.check_call", mock)
    monkeypatch.setattr("solcx.install._download_solc", mock.download)
    yield mock


@pytest.fixture
def cwd():
    """
    Yields the current working directory, and ensures it is reset during teardown.
    """
    cwd = os.getcwd()
    yield cwd
    os.chdir(cwd)


@pytest.fixture
def pragmapatch(monkeypatch):
    """
    Monkeypatches the installed/available versions to ensure consistent testing of
    `install_solc_pragma` and `set_pragma`
    """
    monkeypatch.setattr(
        "solcx.install.get_installed_solc_versions",
        lambda: [
            Version("0.4.2"),
            Version("0.4.11"),
            Version("0.4.25"),
            Version("0.5.0"),
            Version("0.5.4"),
            Version("0.5.7"),
            Version("1.2.3"),
        ],
    )
    monkeypatch.setattr(
        "solcx.install.get_installable_solc_versions",
        lambda: [
            Version("0.4.11"),
            Version("0.4.24"),
            Version("0.4.26"),
            Version("0.5.3"),
            Version("0.6.0"),
        ],
    )
    monkeypatch.setattr("solcx.install.set_solc_version", lambda *args: None)
