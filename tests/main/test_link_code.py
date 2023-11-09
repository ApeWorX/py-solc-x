from pathlib import Path

import pytest

import solcx

source = """pragma solidity >=0.4.11;
library UnlinkedLib {
    function linkMethod(uint _value, uint _multiplier) public returns (uint) {
        return _value * _multiplier;
    }
}

library OtherUnlinkedLib {
    function otherLinkMethod(uint _value, uint _multiplier) public returns (uint) {
        return _value * _multiplier;
    }
}

contract LinkTester {
    function testLibraryLinks(uint amount, uint multiple) external returns (uint) {
        uint a = UnlinkedLib.linkMethod(amount, multiple);
        return OtherUnlinkedLib.otherLinkMethod(a, multiple);
    }
}"""

addr1 = "0x1234567890123456789012345678901234567890"
addr2 = "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"


@pytest.fixture
def bytecode(all_versions):
    yield solcx.compile_source(source)["<stdin>:LinkTester"]["bin"]


def test_unlinked_bytecode(bytecode):
    assert "_" in bytecode
    assert addr1[2:] not in bytecode
    assert addr2[2:] not in bytecode


def test_partial_link(bytecode):
    output = solcx.link_code(bytecode, {"<stdin>:UnlinkedLib": addr1})

    assert output != bytecode
    assert "_" in output
    assert addr1[2:] in output


def test_full_link(bytecode):
    output = solcx.link_code(
        bytecode, {"<stdin>:UnlinkedLib": addr1, "<stdin>:OtherUnlinkedLib": addr2}
    )

    # fully linked bytecode should be able to be interpreted as hex
    assert int(output, 16)

    assert addr1[2:] in output
    assert addr2[2:] in output


def test_solc_binary(wrapper_mock):
    wrapper_mock.expect(solc_binary=Path("path/to/solc"))
    solcx.link_code("0x00", {}, solc_binary=Path("path/to/solc"))


def test_solc_version(wrapper_mock, all_versions):
    solc_binary = solcx.install.get_executable(all_versions)
    wrapper_mock.expect(solc_binary=solc_binary)
    solcx.link_code("0x00", {}, solc_version=all_versions)
