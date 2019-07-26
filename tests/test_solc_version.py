import solcx

import semantic_version


def test_get_solc_version(all_versions):
    version = solcx.get_solc_version()
    assert isinstance(version, semantic_version.Version)


def test_get_solc_version_string(all_versions):
    version = solcx.get_solc_version_string()
    assert isinstance(version, str)
