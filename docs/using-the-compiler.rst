.. _using-the-compiler:

==================
Using the Compiler
==================

py-solc-x provides several functions that you can use to interact with the ``solc`` compiler.

Compiling a Source String
=========================

.. py:function:: solcx.compile_source(source, **kwargs)

    Compile a Solidity contract.

    Compilation is handled via the ``--combined-json`` flag. Depending on the Solidity version used, some keyword arguments may not be available.

    Returns a dict, where each top-level key is a contract. The filename will be ``<stdin>``.

    .. code-block:: python

        >>> import solcx
        >>> solcx.compile_source(
        ...     "contract Foo { function bar() public { return; } }",
        ...     output_values=["abi", "bin-runtime"],
        ...     solc_version="0.7.0"
        ... )
        {
            '<stdin>:Foo': {
                'abi': [{'inputs': [], 'name': 'bar', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}],
                'bin-runtime': '6080604052348015600f57600080fd5b506004361060285760003560e01c8063febb0f7e14602d575b600080fd5b60336035565b005b56fea26469706673582212203cfdbce82ee8eab351107edac2ebb9dbe5c1aa8bd26609b0eedaa105ed3d4dce64736f6c63430007000033'
            }
        }

    **Required Arguments**

        ``source`` str
            Solidity contract to be compiled.

    **Optional py-solc-x Arguments**

        ``solc_binary`` str | Path
            Path of the ``solc`` binary to use. May be given as a string or :py:class:`Path <pathlib.PurePath>` object. If not given, the currently active version is used (as set by :func:`solcx.set_solc_version <solcx.set_solc_version>`)
        ``solc_version`` str | Version
            ``solc`` version to use. May be given as a string or :py:class:`Version <semantic_version.Version>` object. If not given, the currently active version is used. Ignored if ``solc_binary`` is also given.
        ``allow_empty`` bool
            If ``True``, do not raise when no compiled contracts are returned. Defaults to ``False``.

    **Optional Compiler Arguments**

    Depending on the Solidity version used, using some of these arguments may raise ``UnknownOption``. See the documentation for your target Solidity version for more information.

        ``output_values`` List
            Compiler outputs to return. Valid options depend on the version of ``solc``.
            If not given, all possible outputs for the active version are returned.
        ``import_remappings`` Dict | List | str
            Path remappings. May be given as a string or list of strings formatted as
            ``"prefix=path"``, or a dict of ``{"prefix": "path"}``.
        ``base_path`` Path | str
            Use the given path as the root of the source tree instead of the root
            of the filesystem.
        ``allow_paths`` List | Path | str
            A path, or list of paths, to allow for imports.
        ``output_dir`` str
            Creates one file per component and contract/file at the specified directory.
        ``overwrite`` bool
            Overwrite existing files (used in combination with ``output_dir``)
        ``evm_version`` str
            Select the desired EVM version. Valid options depend on the ``solc`` version.
        ``revert_strings`` List | str
            Strip revert (and require) reason strings or add additional debugging
            information.
        ``metadata_hash`` str
            Choose hash method for the bytecode metadata or disable it.
        ``metadata_literal`` bool
            Store referenced sources as literal data in the metadata output.
        ``optimize`` bool
            Enable bytecode optimizer.
        ``optimize_runs`` int
            Set for how many contract runs to optimize. Lower values will optimize
            more for initial deployment cost, higher values will optimize more for
            high-frequency usage.
        ``optimize_yul`` bool
            Enable the yul optimizer.
        ``no_optimize_yul`` bool
            Disable the yul optimizer.
        ``yul_optimizations`` int
            Force yul optimizer to use the specified sequence of optimization steps
            instead of the built-in one.

Compiling Files
===============

.. py:function:: solcx.compile_files(source, **kwargs)

    Compile one or more Solidity source files.

    Compilation is handled via the ``--combined-json`` flag. Depending on the Solidity version used, some keyword arguments may not be available.

    Returns a dict, where each top-level key is a contract.

    .. code-block:: python

        >>> import solcx
        >>> solcx.compile_files(
        ...     ["Foo.sol"],
        ...     output_values=["abi", "bin-runtime"],
        ...     solc_version="0.7.0"
        ... )
        {
            '<stdin>:Foo': {
                'abi': [{'inputs': [], 'name': 'bar', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}],
                'bin-runtime': '6080604052348015600f57600080fd5b506004361060285760003560e01c8063febb0f7e14602d575b600080fd5b60336035565b005b56fea26469706673582212203cfdbce82ee8eab351107edac2ebb9dbe5c1aa8bd26609b0eedaa105ed3d4dce64736f6c63430007000033'
            }
        }

    **Required Arguments**

        ``source_files`` List
            List of Solidity source files to be compiled. Files may be given as strings or :py:class:`Path <pathlib.PurePath>` objects.

    **Optional py-solc-x Arguments**

        ``solc_binary`` str | Path
            Path of the ``solc`` binary to use. May be given as a string or :py:class:`Path <pathlib.PurePath>` object. If not given, the currently active version is used (as set by :func:`solcx.set_solc_version <solcx.set_solc_version>`)
        ``solc_version`` str | Version
            ``solc`` version to use. May be given as a string or :py:class:`Version <semantic_version.Version>` object. If not given, the currently active version is used. Ignored if ``solc_binary`` is also given.
        ``allow_empty`` bool
            If ``True``, do not raise when no compiled contracts are returned. Defaults to ``False``.

    **Optional Compiler Arguments**

    Depending on the Solidity version used, using some of these arguments may raise ``UnknownOption``. See the documentation for your target Solidity version for more information.

        ``output_values`` List
            Compiler outputs to return. Valid options depend on the version of ``solc``.
            If not given, all possible outputs for the active version are returned.
        ``import_remappings`` Dict | List | str
            Path remappings. May be given as a string or list of strings formatted as
            ``"prefix=path"``, or a dict of ``{"prefix": "path"}``.
        ``base_path`` Path | str
            Use the given path as the root of the source tree instead of the root
            of the filesystem.
        ``allow_paths`` List | Path | str
            A path, or list of paths, to allow for imports.
        ``output_dir`` str
            Creates one file per component and contract/file at the specified directory.
        ``overwrite`` bool
            Overwrite existing files (used in combination with ``output_dir``)
        ``evm_version`` str
            Select the desired EVM version. Valid options depend on the ``solc`` version.
        ``revert_strings`` List | str
            Strip revert (and require) reason strings or add additional debugging
            information.
        ``metadata_hash`` str
            Choose hash method for the bytecode metadata or disable it.
        ``metadata_literal`` bool
            Store referenced sources as literal data in the metadata output.
        ``optimize`` bool
            Enable bytecode optimizer.
        ``optimize_runs`` int
            Set for how many contract runs to optimize. Lower values will optimize
            more for initial deployment cost, higher values will optimize more for
            high-frequency usage.
        ``optimize_yul`` bool
            Enable the yul optimizer.
        ``no_optimize_yul`` bool
            Disable the yul optimizer.
        ``yul_optimizations`` int
            Force yul optimizer to use the specified sequence of optimization steps
            instead of the built-in one.

Compiling with the Standard JSON Format
=======================================

.. py:function:: solcx.compile_standard(input_data, **kwargs)

    Compile Solidity contracts using the JSON-input-output interface.

    See the Solidity documentation on `the compiler input-output JSON <https://solidity.readthedocs.io/en/latest/using-the-compiler.html#compiler-input-and-output-json-description>`_ for details on the expected JSON input and output formats.

    **Required Arguments**

        ``input_data`` Dict
            Compiler JSON input.

    **Optional py-solc-x Arguments**

        ``solc_binary`` str | Path
            Path of the ``solc`` binary to use. May be given as a string or :py:class:`Path <pathlib.PurePath>` object. If not given, the currently active version is used (as set by :func:`solcx.set_solc_version <solcx.set_solc_version>`)
        ``solc_version`` str | Version
            ``solc`` version to use. May be given as a string or :py:class:`Version <semantic_version.Version>` object. If not given, the currently active version is used. Ignored if ``solc_binary`` is also given.
        ``allow_empty`` bool
            If ``True``, do not raise when no compiled contracts are returned. Defaults to ``False``.

    **Optional Compiler Arguments**

    Depending on the Solidity version used, using some of these arguments may raise ``UnknownOption``. See the documentation for your target Solidity version for more information.

        ``base_path`` Path | str
            Use the given path as the root of the source tree instead of the root
            of the filesystem.
        ``allow_paths`` List | Path | str
            A path, or list of paths, to allow for imports.
        ``output_dir`` str
            Creates one file per component and contract/file at the specified directory.
        ``overwrite`` bool
            Overwrite existing files (used in combination with ``output_dir``)

Linking Libraries
=================

.. py:function:: solcx.link_code(unlinked_bytecode, libraries, solc_binary=None, solc_version=None)

    Add library addresses into unlinked bytecode.

    See the Solidity documentation on `using the commandline compiler <https://solidity.readthedocs.io/en/latest/using-the-compiler.html#commandline-compiler>`_ for more information on linking libraries.

    Returns the linked bytecode as a string.

    .. code-block:: python

        >>> import solcx
        >>> unlinked_bytecode = "606060405260768060106000396000f3606060405260e060020a6000350463e7f09e058114601a575b005b60187f0c55699c00000000000000000000000000000000000000000000000000000000606090815273__TestA_________________________________90630c55699c906064906000906004818660325a03f41560025750505056"

        >>> solcx.link_code(
        ...     unlinked_bytecode,
        ...     {'TestA': "0xd3cda913deb6f67967b99d67acdfa1712c293601"}
        ... )
        "606060405260768060106000396000f3606060405260e060020a6000350463e7f09e058114601a575b005b60187f0c55699c00000000000000000000000000000000000000000000000000000000606090815273d3cda913deb6f67967b99d67acdfa1712c29360190630c55699c906064906000906004818660325a03f41560025750505056"


    **Required Arguments**

        ``unlinked_bytecode`` str
            Compiled bytecode containing one or more library placeholders.
        ``libraries`` Dict
            Library addresses given as ``{"library name": "address"}``

    **Optional py-solc-x Arguments**

        ``solc_binary`` str | Path
            Path of the ``solc`` binary to use. May be given as a string or :py:class:`Path <pathlib.PurePath>` object. If not given, the currently active version is used (as set by :func:`solcx.set_solc_version <solcx.set_solc_version>`)
        ``solc_version`` str | Version
            ``solc`` version to use. May be given as a string or :py:class:`Version <semantic_version.Version>` object. If not given, the currently active version is used. Ignored if ``solc_binary`` is also given.
