import functools

import pytest
from packaging.version import Version

import solcx
from solcx.exceptions import SolcNotInstalled, UnsupportedVersionError


@pytest.mark.parametrize(
    "pragma,expected",
    [
        ("0.4.11", "0.4.11"),
        ("=0.4.11", "0.4.11"),
        ("^0.4.11", "0.4.25"),
        (">=0.4.0<0.4.25", "0.4.11"),
        (">=0.4.2", "1.2.3"),
        (">=0.4.2<0.5.5", "0.5.4"),
        ("^0.4.2 || 0.5.5", "0.4.25"),
        ("^0.4.2 || >=0.5.4<0.7.0", "0.5.7"),
        ("0.4.2 || >=0.5.4<0.7.0", "0.5.7"),
        ("^0.5.00", "0.5.7"),
        ("=0.4.11 >=0.4.0 <0.5.0 >=0.4.2 <0.5.0", "0.4.11"),
    ],
)
def test_set_solc_version_pragma(pragmapatch, pragma, expected):
    set_pragma = functools.partial(solcx.set_solc_version_pragma, check_new=True)
    assert set_pragma(f"pragma solidity {pragma};") == Version(expected)


def test_set_solc_version_pragma_not_installed(pragmapatch):
    set_pragma = functools.partial(solcx.set_solc_version_pragma, check_new=True)
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
    with pytest.raises(UnsupportedVersionError):
        install_pragma("pragma solidity ^0.7.1;")


def test_get_solc_version():
    version = solcx.get_solc_version()
    version_with_hash = solcx.get_solc_version(with_commit_hash=True)

    assert version != version_with_hash
    assert version == Version(version_with_hash.base_version)
