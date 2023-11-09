# py-solc-x

[![Pypi Status](https://img.shields.io/pypi/v/py-solc-x.svg)](https://pypi.org/project/py-solc-x/) [![Build Status](https://img.shields.io/github/workflow/status/iamdefinitelyahuman/py-solc-x/py-solc-x%20workflow)](https://github.com/iamdefinitelyahuman/py-solc-x/actions) [![Coverage Status](https://img.shields.io/codecov/c/github/iamdefinitelyahuman/py-solc-x)](https://codecov.io/gh/iamdefinitelyahuman/py-solc-x)

Python wrapper and version management tool for the `solc` Solidity compiler.

Forked from [`py-solc`](https://github.com/ethereum/py-solc).

## Features

- Full support for Solidity `>=0.4.11`
- Install Solidity on Linux, OSX and Windows
- Compile Solidity from source on Linux and OSX

## Dependencies

Py-solc-x allows the use of multiple versions of solc, and can install or compile them as needed. If you wish to compile from source you must first insall the required [solc dependencies](https://solidity.readthedocs.io/en/latest/installing-solidity.html#building-from-source).

## Installation

### via `pip`

```bash
pip install py-solc-x
```

### via `setuptools`

```bash
git clone https://github.com/iamdefinitelyahuman/py-solc-x.git
cd py-solc-x
python3 setup.py install
```

## Documentation

Documentation is hosted at [Read the Docs](https://solcx.readthedocs.io/en/latest/).

## Testing

Py-solc-x is tested on Linux, OSX and Windows with solc versions `>=0.4.11`.

To run the test suite:

```bash
pytest tests/
```

By default, the test suite installs all available `solc` versions for your OS. If you only wish to test against already installed versions, include the `--no-install` flag.

## Contributing

Help is always appreciated! Feel free to open an issue if you find a problem, or a pull request if you've solved an issue.

Please check out our [Contribution Guide](CONTRIBUTING.md) prior to opening a pull request, and join the Brownie [Gitter channel](https://gitter.im/eth-brownie/community) if you have any questions.

## License

This project is licensed under the [MIT license](LICENSE).
