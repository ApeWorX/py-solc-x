=============================
The Low-Level Process Wrapper
=============================

Along with the :ref:`main compiler functions <using-the-compiler>`, you can also directly call ``solc`` using the low-level wrapper.

.. py:function:: solc_wrapper(solc_binary=None, stdin=None, source_files=None, import_remappings=None, success_return_code=None, **kwargs)

    Wrapper function for calling to ``solc``.

    Returns the process ``stdout`` as a string, ``stderr`` as a string, the full command executed as a list of strings, and the completed :py:class:`Popen <subprocess.Popen>` object used to call ``solc``.

    **Arguments**

        ``solc_binary`` : Path | str
            Location of the ``solc`` binary. If not given, the current default binary is used.
        ``stdin`` : str
            Input to pass to ``solc`` via stdin
        ``source_files`` List | Path | str
            Solidity source file, or list of source files, to be compiled. Files may be given as strings or :py:class:`Path <pathlib.PurePath>` objects.
        ``import_remappings`` : Dict | List | str
            Path remappings. May be given as a string or list of strings formatted as ``"prefix=path"``
            or a dict of ``{"prefix": "path"}``
        ``success_return_code`` : int
            Expected exit code. Raises ``SolcError`` if the process returns a different value. Defaults to ``0``.
        ``**kwargs`` Any
            Flags to be passed to `solc`. Keywords are converted to flags by prepending ``--`` and replacing ``_`` with ``-``, for example the keyword ``evm_version`` becomes ``--evm-version``. Values may be given in the following formats:

            * ``False`` or ``None``: The flag is ignored
            * ``True``: The flag is passed to the compiler without any arguments
            * ``str``: The value is given as an argument without any modification
            * ``int``: The value is converted to a string
            * ``Path``: The value is converted to a string via :py:meth:`Path.as_posix <pathlib.PurePath.as_posix>`
            * ``List`` or ``Tuple``: Elements in the sequence are converted to strings and joined with ``,``
