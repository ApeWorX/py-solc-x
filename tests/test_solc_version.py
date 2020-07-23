#!/usr/bin/python3

import functools

import pytest
from semantic_version import Version

import solcx
from solcx.exceptions import SolcNotInstalled


@pytest.fixture
def pragmapatch(monkeypatch):
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
        "solcx.install.get_available_solc_versions",
        lambda: [
            Version("0.4.11"),
            Version("0.4.24"),
            Version("0.4.26"),
            Version("0.5.3"),
            Version("0.6.0"),
        ],
    )


def test_get_solc_version(all_versions):
    v = solcx.get_solc_version()
    assert isinstance(v, Version)


def test_set_solc_version_pragma(pragmapatch):
    set_pragma = functools.partial(solcx.set_solc_version_pragma, check_new=True)
    set_pragma("pragma solidity 0.4.11;")
    assert solcx.install.solc_version == Version("0.4.11")
    set_pragma("pragma solidity ^0.4.11;")
    assert solcx.install.solc_version == Version("0.4.25")
    set_pragma("pragma solidity >=0.4.0<0.4.25;")
    assert solcx.install.solc_version == Version("0.4.11")
    set_pragma("pragma solidity >=0.4.2;")
    assert solcx.install.solc_version == Version("1.2.3")
    set_pragma("pragma solidity >=0.4.2<0.5.5;")
    assert solcx.install.solc_version == Version("0.5.4")
    set_pragma("pragma solidity ^0.4.2 || 0.5.5;")
    assert solcx.install.solc_version == Version("0.4.25")
    set_pragma("pragma solidity ^0.4.2 || >=0.5.4<0.7.0;")
    assert solcx.install.solc_version == Version("0.5.7")
    with pytest.raises(SolcNotInstalled):
        set_pragma("pragma solidity ^0.7.1;")


def test_install_solc_version_pragma(pragmapatch):
    install_pragma = functools.partial(solcx.install_solc_pragma, install=False)
    assert install_pragma("pragma solidity ^0.4.11;") == Version("0.4.26")
    assert install_pragma("pragma solidity >=0.4.0<0.4.25;") == Version("0.4.24")
    assert install_pragma("pragma solidity >=0.4.2;") == Version("0.6.0")
    assert install_pragma("pragma solidity >=0.4.2<0.5.5;") == Version("0.5.3")
    assert install_pragma("pragma solidity ^0.4.2 || 0.5.5;") == Version("0.4.26")
    assert install_pragma("pragma solidity ^0.4.2 || >=0.5.4<0.7.0;") == Version("0.6.0")
    with pytest.raises(ValueError):
        install_pragma("pragma solidity ^0.7.1;")
