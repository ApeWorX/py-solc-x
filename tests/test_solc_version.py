#!/usr/bin/python3

import solcx

from semantic_version import Version


def test_solc_supports_standard_json_interface(monkeypatch):
    monkeypatch.setattr('solcx.main.get_solc_version', lambda: Version("0.5.0"))
    assert solcx.main.solc_supports_standard_json_interface()
    monkeypatch.setattr('solcx.main.get_solc_version', lambda: Version("0.4.11"))
    assert solcx.main.solc_supports_standard_json_interface()
    monkeypatch.setattr('solcx.main.get_solc_version', lambda: Version("0.4.10"))
    assert not solcx.main.solc_supports_standard_json_interface()


def test_get_solc_version(all_versions):
    v = solcx.get_solc_version()
    assert isinstance(v, Version)


def test_get_solc_version_string(all_versions):
    v = solcx.get_solc_version_string()
    assert isinstance(v, str)
