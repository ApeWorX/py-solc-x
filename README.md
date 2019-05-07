# py-solc-x

Python wrapper around the `solc` Solidity compiler with `0.5.x` support.

Forked from [py-solc](https://github.com/ethereum/py-solc).

## Dependencies

Py-solc-x allows the use of multiple versions of solc and installs them as needed. You must have all required [solc dependencies](https://solidity.readthedocs.io/en/latest/installing-solidity.html#building-from-source) installed for it to work properly.

Versions `>=0.4.11` may be installed, however only versions `>=0.4.2` are supported and tested.

## Quickstart

Installation

```sh
pip install py-solc-x
```

## Installing the `solc` Executable

The first time py-solc-x is imported it will automatically check for an installed version of solc on your system. If none is found, you must manually install via `solcx.install_solc`

```python
>>> from solcx import install_solc
>>> install_solc('v0.4.25')
```

Or via the command line:

```bash
$ python -m solcx.install v0.4.25
```

Py-solc-x defaults to the most recent installed version set as the active one. To check or modify the active version:

```python
>>> from solcx import get_solc_version, set_solc_version
>>> get_solc_version()
Version('0.5.7+commit.6da8b019.Linux.gpp')
>>> set_solc_version('v0.4.25')
>>>
```

To install the highest compatible version based on the pragma version string:

```python
>>> from solcx import install_solc_pragma
>>> install_solc_pragma('^0.4.20 || >0.5.5 <0.7.0')
```

To set the version based on the pragma version string - this will use the highest compatible version installed, if you have a compatible version installed, or it will install the highest compatible version:

```python
>>> from solcx import set_solc_version_pragma
>>> set_solc_version_pragma('^0.4.20 || >0.5.5 <0.7.0')
```

To view available and installed versions:

```python
>>> from solcx import get_installed_solc_versions, get_available_solc_versions
>>> get_installed_solc_versions()
['v0.4.25', 'v0.5.3']
>>> get_available_solc_versions()
['v0.5.8', 'v0.5.7', 'v0.5.6', 'v0.5.5', 'v0.5.4', 'v0.5.3', 'v0.5.2', 'v0.5.1', 'v0.5.0', 'v0.4.25', 'v0.4.24', 'v0.4.23', 'v0.4.22', 'v0.4.21', 'v0.4.20', 'v0.4.19', 'v0.4.18', 'v0.4.17', 'v0.4.16', 'v0.4.15', 'v0.4.14', 'v0.4.13', 'v0.4.12', 'v0.4.11']
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
>>> from solcx import compile_source, compile_files, link_code
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
>>> unlinked_code = "606060405260768060106000396000f3606060405260e060020a6000350463e7f09e058114601a575b005b60187f0c55699c00000000000000000000000000000000000000000000000000000000606090815273__TestA_________________________________90630c55699c906064906000906004818660325a03f41560025750505056"
>>> link_code(unlinked_code, {'TestA': '0xd3cda913deb6f67967b99d67acdfa1712c293601'})
... "606060405260768060106000396000f3606060405260e060020a6000350463e7f09e058114601a575b005b60187f0c55699c00000000000000000000000000000000000000000000000000000000606090815273d3cda913deb6f67967b99d67acdfa1712c29360190630c55699c906064906000906004818660325a03f41560025750505056"
```

## Import Path Remappings

`solc` provides path aliasing allow you to have more reusable project configurations.

You can use this like:

```python
>>> from solcx import compile_source, compile_files, link_code

>>> compile_files([source_file_path], import_remappings=["zeppeling=/my-zeppelin-checkout-folder"])
```

[More information about solc import aliasing](http://solidity.readthedocs.io/en/develop/layout-of-source-files.html#paths) 

## Development

This project was recently forked from [py-solc](https://github.com/ethereum/py-solc) and should be considered a beta. Comments, questions, criticisms and pull requests are welcomed.

### Tests

Tests have not been updated from py-solc and are currently failing. If you would like to contribute by updating them, please don't hesitate :)

## License

This project is licensed under the [MIT license](LICENSE).
