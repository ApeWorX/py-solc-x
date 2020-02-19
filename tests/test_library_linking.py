#!/usr/bin/python3

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
def bytecode():
    yield solcx.compile_source(source)["<stdin>:LinkTester"]["bin"]


def test_partial_link(all_versions, bytecode):
    assert "_" in bytecode
    assert addr1[2:] not in bytecode
    output = solcx.link_code(bytecode, {"<stdin>:UnlinkedLib": addr1})
    assert output != bytecode
    assert "_" in output
    assert addr1[2:] in output


def test_full_link(all_versions, bytecode):
    assert "_" in bytecode
    assert addr1[2:] not in bytecode
    assert addr2[2:] not in bytecode
    output = solcx.link_code(
        bytecode, {"<stdin>:UnlinkedLib": addr1, "<stdin>:OtherUnlinkedLib": addr2}
    )
    assert output != bytecode
    assert "_" not in output
    assert addr1[2:] in output
    assert addr2[2:] in output
