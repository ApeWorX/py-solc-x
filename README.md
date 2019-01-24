# py-solc-x

Python wrapper around the `solc` Solidity compiler with `0.5.x` support.

Forked from [py-solc](https://github.com/ethereum/py-solc).

## Dependencies

This library allows the use of multiple versions of solc, and installs them as needed. You must have all required [solc dependencies](https://solidity.readthedocs.io/en/latest/installing-solidity.html#building-from-source) installed for it to work properly.

Versions `>=0.4.11` may be installed, however only versions `>=0.4.2` are supported and tested.

## Quickstart

Installation

```sh
pip install py-solc-x
```

## Installing the `solc` Executable

The first time py-solc-x is imported it will automatically install the latest version of solc. If you wish to install a different version you may do so from within python:

```python
>>> from solcx import install_solc
>>> install_solc('v0.4.25')
```

Or via the command line:

```bash
$ python -m solcx.install v0.4.25
```

You can also view available versions or change the active version of solc:

```python
>>> from solcx import get_installed_solc_versions, set_solc_version
>>> get_installed_solc_versions()
['v0.4.25', 'v0.5.3']

>>> set_solc_version('v0.4.25)
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
...     'sources': {'Foo.sol': 'urls': ["/path/to/my/sources/Foo.sol"]},
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

### Running the tests

> Tests have not been updated from py-solc and will likely fail.

You can run the tests with:

```sh
py.test tests
```

Or you can install `tox` to run the full test suite.

## License

This project is licensed under the [MIT license](LICENSE).