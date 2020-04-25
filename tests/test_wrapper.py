#!/usr/bin/python3

import subprocess

import pytest

import solcx


class PopenPatch:
    def __init__(self):
        self.proc = subprocess.Popen
        self.args = []

    def __call__(self, cmd, **kwargs):
        assert cmd[0] == solcx.install.get_executable()
        for i in self.args:
            assert i in cmd
        return self.proc(cmd, **kwargs)

    def expect(self, *args):
        self.args = [f"--{i.replace('_', '-')}" for i in args]


@pytest.fixture
def popen(monkeypatch):
    p = PopenPatch()
    monkeypatch.setattr("subprocess.Popen", p)
    yield p


@pytest.fixture(autouse=True)
def setup(all_versions):
    pass


def test_help(popen):
    popen.expect("help")
    solcx.wrapper.solc_wrapper(help=True, success_return_code=1)


def test_boolean_kwargs(popen, foo_source):
    kwargs = [
        "version",
        "optimize",
        "gas",
        "ast_json",
        "asm",
        "asm_json",
        "opcodes",
        "bin",
        "bin_runtime",
        "abi",
        "hashes",
        "userdoc",
        "devdoc",
        "standard_json",
    ]
    for value in kwargs:
        popen.expect(value)
        solcx.wrapper.solc_wrapper(stdin=foo_source, **{value: True})


def test_removed_kwargs(popen, foo_source):
    solc_minor_version = solcx.get_solc_version().minor
    kwargs = [("ast", 6), ("clone_bin", 5), ("formal", 5)]
    for value, minor in kwargs:
        popen.expect(value)
        if solc_minor_version >= minor:
            with pytest.raises(AttributeError):
                solcx.wrapper.solc_wrapper(stdin=foo_source, **{value: True})
        else:
            solcx.wrapper.solc_wrapper(stdin=foo_source, **{value: True})


def test_value_kwargs(popen, foo_source):
    kwargs = [
        ("optimize_runs", 200),
        ("libraries", "libraries:0x1234567890123456789012345678901234567890"),
        ("output_dir", "."),
        ("combined_json", "abi"),
        ("allow_paths", "."),
    ]
    for value in kwargs:
        popen.expect(value[0])
        solcx.wrapper.solc_wrapper(stdin=foo_source, **{value[0]: value[1]})
