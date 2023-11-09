# Using the Compiler

py-solc-x provides several functions that you can use to interact with the `solc` compiler.

## Compiling a Source String

Compile a Solidity contract.
Compilation is handled via the `--combined-json` flag. Depending on the Solidity version used, some keyword arguments may not be available.
Returns a dict, where each top-level key is a contract. The filename will be `<stdin>`.

```python
import solcx

solcx.compile_source(
    "contract Foo { function bar() public { return; } }",
    output_values=["abi", "bin-runtime"],
    solc_version="0.7.0"
)
```

## Compiling Files

Compile one or more Solidity source files.
Compilation is handled via the `--combined-json` flag.
Depending on the Solidity version used, some keyword arguments may not be available.
Returns a dict, where each top-level key is a contract.

```python
import solcx

solcx.compile_files(
    ["Foo.sol"],
    output_values=["abi", "bin-runtime"],
    solc_version="0.7.0"
)
```

## Compiling with the Standard JSON Format

Compile Solidity contracts using the JSON-input-output interface.
See the Solidity documentation on [the compiler input-output JSON](https://solidity.readthedocs.io/en/latest/using-the-compiler.html#compiler-input-and-output-json-description) for details on the expected JSON input and output formats.

```python
import solcx

solcx.compile_standard(
    {},
    solc_version="0.7.0"
)
```

## Linking Libraries

Add library addresses into unlinked bytecode.
See the Solidity documentation on [using the commandline compiler](https://solidity.readthedocs.io/en/latest/using-the-compiler.html#commandline-compiler%3E) for more information on linking libraries.

```python
import solcx

unlinked_bytecode = "606060405260768060106000396000f3606060405260e060020a6000350463e7f09e058114601a575b005b60187f0c55699c00000000000000000000000000000000000000000000000000000000606090815273__TestA_________________________________90630c55699c906064906000906004818660325a03f41560025750505056"

solcx.link_code(
    unlinked_bytecode,
    {'TestA': "0xd3cda913deb6f67967b99d67acdfa1712c293601"}
)
```
