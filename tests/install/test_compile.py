import os

import pytest

import solcx
from solcx.exceptions import SolcInstallationError


@pytest.mark.skipif("sys.platform != 'win32'")
def test_fails_on_windows():
    with pytest.raises(OSError):
        solcx.compile_solc("latest")


@pytest.mark.skipif("sys.platform == 'win32'")
def test_compile_already_installed():
    version = solcx.get_installed_solc_versions()[0]
    assert solcx.compile_solc("latest") == version


@pytest.mark.skipif("sys.platform == 'win32'")
def test_compile(compile_mock, solc_binary, cwd):
    version = solcx.wrapper.get_solc_version(solc_binary)
    solcx.compile_solc(version)

    assert os.getcwd() == cwd
    assert solcx.get_installed_solc_versions() == [version]


@pytest.mark.skipif("sys.platform == 'win32'")
def test_compile_install_deps_fails(compile_mock, solc_binary, cwd):
    version = solcx.wrapper.get_solc_version(solc_binary)
    compile_mock.raise_on("sh")
    solcx.compile_solc(version)

    assert os.getcwd() == cwd
    assert solcx.get_installed_solc_versions() == [version]


@pytest.mark.skipif("sys.platform == 'win32'")
def test_compile_install_cmake_fails(compile_mock, solc_binary, cwd):
    compile_mock.raise_on("cmake")
    with pytest.raises(SolcInstallationError):
        solcx.compile_solc("latest")

    assert os.getcwd() == cwd


@pytest.mark.skipif("sys.platform == 'win32'")
def test_compile_install_make_fails(compile_mock, solc_binary, cwd):
    compile_mock.raise_on("make")
    with pytest.raises(SolcInstallationError):
        solcx.compile_solc("latest")

    assert os.getcwd() == cwd
