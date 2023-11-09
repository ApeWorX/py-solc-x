# Solidity Version Management

## Installation Folder

By default, `solc` versions are installed at `~/.solcx/`.
Each installed version is named using the following pattern: `solc-v[MAJOR].[MINOR].[PATH]`.

If you wish to install to a different directory you can specify it with the `SOLCX_BINARY_PATH` environment variable.
You can also give a custom directory to most installation functions using the optional `solcx_binary_path` keyword argument.

```python
import solcx
solcx.get_solcx_install_folder()
```

## Getting and Setting the Active Version

When py-solc-x is imported, it attempts to locate an installed version of `solc` using `which` on Linux or OSX systems, or `where.exe` on Windows.
If found, this version is set as the active version.
If not found, it uses the latest version that has been installed by py-solc-x.

## Getting the Active Version

Use the following methods to check the active `solc` version:

```python
import solcx

solcx.get_solc_version()
solcx.get_solc_version(with_commit_hash=True)

# Also, get the path to the executable:
solcx.install.get_executable()
```

## Setting the Active Version

Set the currently active `solc` version:

```python
import solcx

solcx.set_solc_version('0.5.0')
```

Set the currently active `solc` binary based on a pragma statement.
The newest installed version that matches the pragma is chosen.

```python
import solcx

solcx.set_solc_version_pragma('pragma solidity ^0.5.0;')
```

## Importing Already-Installed Versions

Search for and copy installed `solc` versions into the local installation folder.
This function is especially useful on OSX, to access Solidity versions that you have installed from homebrew and where a precompiled binary is not available.

```python
import solcx

solcx.import_installed_solc()
```

## Installing Solidity

py-solc-x downloads and installs precompiled binaries from [solc-bin.ethereum.org](solc-bin.ethereum.org).
Different binaries are available depending on your operating system.

## Getting Installable Versions

```python
import solcx

solcx.get_installable_solc_versions()
```

## Installing Precompiled Binaries

Download and install a precompiled `solc` binary:

```python
import solcx

solcx.install_solc(version="latest", show_progress=False, solcx_binary_path=None)
```

## Building from Source

When a precompiled version of Solidity isn't available for your operating system, you may still install it by building from the source code.
Source code is downloaded from [GitHub](https://github.com/ethereum/solidity/releases).

**NOTE**: If you wish to compile from source you must first install the required [solc dependencies](https://solidity.readthedocs.io/en/latest/installing-solidity.html#building-from-source).

## Getting Compilable Versions

Return a list of all `solc` versions that can be installed by py-solc-x.

```python
import solcx

solcx.get_compilable_solc_versions()
```

## Compiling Solidity from Source

Install a version of `solc` by downloading and compiling source code.

```python
import solcx

solcx.compile_solc("0.8.17", show_progress=False, solcx_binary_path=None)
```
