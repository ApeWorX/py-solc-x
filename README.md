# py-solc-x

[![Pypi Status](https://img.shields.io/pypi/v/py-solc-x.svg)](https://pypi.org/project/py-solc-x/) [![Build Status](https://img.shields.io/travis/com/iamdefinitelyahuman/py-solc-x.svg)](https://travis-ci.com/iamdefinitelyahuman/py-solc-x) [![Coverage Status](https://coveralls.io/repos/github/iamdefinitelyahuman/py-solc-x/badge.svg?branch=master)](https://coveralls.io/github/iamdefinitelyahuman/py-solc-x?branch=master)

Python wrapper around the `solc` Solidity compiler with `0.5.x` and `0.6.x` support.

Forked from [py-solc](https://github.com/ethereum/py-solc).

## Dependencies

Py-solc-x allows the use of multiple versions of solc and installs them as needed. You must have all required [solc dependencies](https://solidity.readthedocs.io/en/latest/installing-solidity.html#building-from-source) installed for it to work properly.

## Supported Versions

Py-solc-x can install the following solc versions:

* Linux and Windows: `>=0.4.11`
* OSX: `>=0.5.0`

`0.4.x` versions are available on OSX if they have been [installed via brew](https://github.com/ethereum/homebrew-ethereum), but cannot be installed directly by py-solc-x.

## Quickstart

Installation

```sh
pip install py-solc-x
```

## Installing the `solc` Executable

The first time py-solc-x is imported it will automatically check for an installed version of solc on your system. If none is found, you must manually install via `solcx.install_solc`:

```python
>>> from solcx import install_solc
>>> install_solc('v0.4.25')
```

Or via the command line:

```bash
python -m solcx.install v0.4.25
```

By default, `solc` versions are installed at `~/.solcx/`. If you wish to use a different directory you can specify it with the `SOLCX_BINARY_PATH` environment variable.

## Setting the `solc` Version

Py-solc-x defaults to the most recent installed version set as the active one. To check or modify the active version:

```python
>>> from solcx import get_solc_version, set_solc_version
>>> get_solc_version()
Version('0.5.7+commit.6da8b019.Linux.gpp')
>>> set_solc_version('v0.4.25')
>>>
```

You can also set the version based on the pragma version string. The highest compatible version will be used:

```python
>>> from solcx import set_solc_version_pragma
>>> set_solc_version_pragma('^0.4.20 || >0.5.5 <0.7.0')
Using solc version 0.5.8
>>> set_solc_version_pragma('^0.4.20 || >0.5.5 <0.7.0', check_new=True)
Using solc version 0.5.8
Newer compatible solc version exists: 0.6.0
```

To view available and installed versions:

```python
>>> from solcx import get_installed_solc_versions, get_available_solc_versions
>>> get_installed_solc_versions()
['v0.4.25', 'v0.5.3', 'v0.6.0']
>>> get_available_solc_versions()
['v0.6.0', 'v0.5.15', 'v0.5.14', 'v0.5.13', 'v0.5.12', 'v0.5.11', 'v0.5.10', 'v0.5.9', 'v0.5.8', 'v0.5.7', 'v0.5.6', 'v0.5.5', 'v0.5.4', 'v0.5.3', 'v0.5.2', 'v0.5.1', 'v0.5.0', 'v0.4.25', 'v0.4.24', 'v0.4.23', 'v0.4.22', 'v0.4.21', 'v0.4.20', 'v0.4.19', 'v0.4.18', 'v0.4.17', 'v0.4.16', 'v0.4.15', 'v0.4.14', 'v0.4.13', 'v0.4.12', 'v0.4.11']
```

To install the highest compatible version based on the pragma version string:

```python
>>> from solcx import install_solc_pragma
>>> install_solc_pragma('^0.4.20 || >0.5.5 <0.7.0')
```

## Standard JSON Compilation

Use the `solcx.compile_standard` function to make use of the [standard-json](http://solidity.readthedocs.io/en/latest/using-the-compiler.html#compiler-input-and-output-json-description) compilation feature.

```python
>>> from solcx import compile_standard
>>> compile_standard({
...     'language': 'Solidity',
...     'sources': {'Foo.sol': 'content': "...."},
... })
{
    'contracts': {...},
    'sources': {...},
    'errors': {...},
}
>>> compile_standard({
...     'language': 'Solidity',
...     'sources': {'Foo.sol': {'urls': ["/path/to/my/sources/Foo.sol"]}},
... }, allow_paths="/path/to/my/sources")
{
    'contracts': {...},
    'sources': {...},
    'errors': {...},
}
```

## Legacy Combined JSON compilation

```python
>>> from solcx import compile_source, compile_files
>>> compile_source("contract Foo { function Foo() {} }")
{
    'Foo': {
        'abi': [{'inputs': [], 'type': 'constructor'}],
        'code': '0x60606040525b5b600a8060126000396000f360606040526008565b00',
        'code_runtime': '0x60606040526008565b00',
        'source': None,
        'meta': {
            'compilerVersion': '0.3.5-9da08ac3',
            'language': 'Solidity',
            'languageVersion': '0',
        },
    },
}
>>> compile_files(["/path/to/Foo.sol", "/path/to/Bar.sol"])
{
    'Foo': {
        'abi': [{'inputs': [], 'type': 'constructor'}],
        'code': '0x60606040525b5b600a8060126000396000f360606040526008565b00',
        'code_runtime': '0x60606040526008565b00',
        'source': None,
        'meta': {
            'compilerVersion': '0.3.5-9da08ac3',
            'language': 'Solidity',
            'languageVersion': '0',
        },
    },
    'Bar': {
        'abi': [{'inputs': [], 'type': 'constructor'}],
        'code': '0x60606040525b5b600a8060126000396000f360606040526008565b00',
        'code_runtime': '0x60606040526008565b00',
        'source': None,
        'meta': {
            'compilerVersion': '0.3.5-9da08ac3',
            'language': 'Solidity',
            'languageVersion': '0',
        },
    },
}
```

## Unlinked Libraries

```python
>>> from solcx import link_code
>>> unlinked_bytecode = "606060405260768060106000396000f3606060405260e060020a6000350463e7f09e058114601a575b005b60187f0c55699c00000000000000000000000000000000000000000000000000000000606090815273__TestA_________________________________90630c55699c906064906000906004818660325a03f41560025750505056"
>>> link_code(unlinked_bytecode, {'TestA': '0xd3cda913deb6f67967b99d67acdfa1712c293601'})
... "606060405260768060106000396000f3606060405260e060020a6000350463e7f09e058114601a575b005b60187f0c55699c00000000000000000000000000000000000000000000000000000000606090815273d3cda913deb6f67967b99d67acdfa1712c29360190630c55699c906064906000906004818660325a03f41560025750505056"
```

## Import Path Remappings

`solc` provides path aliasing allow you to have more reusable project configurations.

You can use this like:

```python
>>> from solcx import compile_files

>>> compile_files([source_file_path], import_remappings=["zeppeling=/my-zeppelin-checkout-folder"])
```

[More information about solc import aliasing](http://solidity.readthedocs.io/en/latest/layout-of-source-files.html#paths)

## Development

This project was forked from [py-solc](https://github.com/ethereum/py-solc) and should be considered a beta. Comments, questions, criticisms and pull requests are welcomed.

### Tests

Py-solc-x is tested on Linux and Windows with solc versions ``>=0.4.11``.

To run the test suite:

```bash
pytest tests/
```

By default, the test suite installs all available solc versions for your OS. If you only wish to test against already installed versions, include the `--no-install` flag.

## License

This project is licensed under the [MIT license](LICENSE).
