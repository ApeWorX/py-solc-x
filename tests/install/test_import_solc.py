#!/usr/bin/python3

import solcx


def test_import_solc(monkeypatch, solc_binary, nosolc):
    version = solcx.wrapper._get_solc_version(solc_binary)

    monkeypatch.setattr("solcx.install._get_which_solc", lambda: solc_binary)
    assert solcx.import_installed_solc() == [version]

    assert nosolc.joinpath(f"solc-v{version}").exists()


def test_import_solc_fails_after_importing(monkeypatch, solc_binary, nosolc):
    count = 0
    version = solcx.wrapper._get_solc_version(solc_binary)

    def version_mock(*args):
        # the first version call succeeds, the second attempt fails
        # this mocks a solc binary that no longer works after being copied
        nonlocal count
        if not count:
            count += 1
            return version
        raise Exception

    monkeypatch.setattr("solcx.install._get_which_solc", lambda: solc_binary)
    monkeypatch.setattr("solcx.wrapper._get_solc_version", version_mock)

    assert solcx.import_installed_solc() == []
    assert not nosolc.joinpath(solc_binary.name).exists()
