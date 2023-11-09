import subprocess
from typing import Mapping, cast

import pytest
from packaging.version import Version

import solcx
from solcx.exceptions import UnknownOption, UnknownValue


class PopenPatch:
    def __init__(self):
        self.proc = subprocess.Popen
        self.args = []

    def __call__(self, cmd, **kwargs):
        if cmd[1] == "--version":
            return self.proc(cmd, **kwargs)
        assert cmd[0] == str(solcx.install.get_executable())
        for i in self.args:
            assert i in cmd
        return self.proc(cmd, **kwargs)

    def expect(self, *args):
        self.args = [f"--{i.replace('_', '-')}" for i in args]


@pytest.fixture
def popen(monkeypatch):
    patch = PopenPatch()
    monkeypatch.setattr("subprocess.Popen", patch)
    yield patch


@pytest.fixture(autouse=True)
def setup(all_versions):
    pass


def test_help(popen):
    popen.expect("help")
    solcx.wrapper.solc_wrapper(help=True)


@pytest.mark.parametrize(
    "kwarg",
    [
        "help",
        "version",
        "optimize",
        "gas",
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
    ],
)
def test_boolean_kwargs(popen, foo_source, kwarg):
    popen.expect(kwarg)
    solcx.wrapper.solc_wrapper(stdin=foo_source, **cast(Mapping, {kwarg: True}))


@pytest.mark.parametrize(
    "kwarg,min_solc",
    [("ast", "0.6.0"), ("clone_bin", "0.5.0"), ("formal", "0.5.0"), ("ast_json", "0.8.2")],
)
def test_removed_kwargs(popen, foo_source, kwarg, min_solc):
    popen.expect(kwarg)
    data = cast(Mapping, {kwarg: True})
    version = solcx.get_solc_version()
    if version >= Version(min_solc):
        with pytest.raises(UnknownOption):
            solcx.wrapper.solc_wrapper(stdin=foo_source, **data)
    else:
        solcx.wrapper.solc_wrapper(stdin=foo_source, **data)


def test_unknown_value(foo_source, all_versions):
    expected = UnknownValue if all_versions >= Version("0.4.21") else UnknownOption
    with pytest.raises(expected):
        solcx.wrapper.solc_wrapper(stdin=foo_source, evm_version="potato")


@pytest.mark.parametrize(
    "kwarg,value",
    [
        ("optimize_runs", 200),
        ("libraries", "libraries:0x1234567890123456789012345678901234567890"),
        ("output_dir", "."),
        ("combined_json", "abi"),
        ("allow_paths", "."),
    ],
)
def test_value_kwargs(popen, foo_source, kwarg, value):
    popen.expect(kwarg)
    data = cast(Mapping, {kwarg: value})
    solcx.wrapper.solc_wrapper(stdin=foo_source, **data)
