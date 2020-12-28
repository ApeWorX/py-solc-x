===========================
Solidity Version Management
===========================

Installation Folder
===================

By default, ``solc`` versions are installed at ``~/.solcx/``. Each installed version is named using the following pattern: ``solc-v[MAJOR].[MINOR].[PATH]``

If you wish to install to a different directory you can specify it with the ``SOLCX_BINARY_PATH`` environment variable. You can also give a custom directory to most installation functions using the optional ``solcx_binary_path`` keyword argument.

.. py:function:: solcx.get_solcx_install_folder(solcx_binary_path=None)

    Return the directory where py-solc-x stores installed ``solc`` binaries.

    .. code-block:: python

        >>> solcx.get_solcx_install_folder()
        PosixPath('/home/computer/.solcx')

Getting and Setting the Active Version
======================================

When py-solc-x is imported, it attempts to locate an installed version of ``solc`` using ``which`` on Linux or OSX systems, or ``where.exe`` on Windows. If found, this version is set as the active version. If not found, it uses the latest version that has been installed by py-solc-x.


Getting the Active Version
--------------------------

Use the following methods to check the active ``solc`` version:

.. py:function:: solcx.get_solc_version(with_commit_hash=False)

    Return the version of the current active ``solc`` binary, as a :py:class:`Version <semantic_version.Version>` object.

    * ``with_commit_hash``: If ``True``, the returned version includes the commit hash

    .. code-block:: python

        >>> solcx.get_solc_version()
        Version('0.7.0')

        >>> solcx.get_solc_version(True)
        Version('0.7.0+commit.9e61f92b')


.. py:function:: solcx.install.get_executable(version=None, solcx_binary_path=None)

    Return a :py:class:`Path <pathlib.PurePath>` object for a ``solc`` binary.

    If no arguments are given, returns the current active version. If a version is specified, returns the installed binary matching the given version.

    Raises ``SolcNotInstalled`` if no binary is found.

    .. code-block:: python

        >>> solcx.install.get_executable()
        PosixPath('/usr/bin/solc')

.. py:function:: solcx.get_installed_solc_versions(solcx_binary_path=None)

    Return a list of currently installed ``solc`` versions.

    .. code-block:: python

        >>> solcx.get_installed_solc_versions()
        [Version('0.7.0'), Version('0.6.8'), Version('0.6.3'), Version('0.5.7'), Version('0.4.25')]

Setting the Active Version
--------------------------

.. py:function:: solcx.set_solc_version(version, silent=False, solcx_binary_path=None)

    Set the currently active ``solc`` version.

    .. code-block:: python

        >>> solcx.set_solc_version('0.5.0')

.. py:function:: solcx.set_solc_version_pragma(pragma_string, silent=False, check_new=False)

    Set the currently active ``solc`` binary based on a pragma statement.

    The newest installed version that matches the pragma is chosen. Raises ``SolcNotInstalled`` if no installed versions match.

    .. code-block:: python

        >>> solcx.set_solc_version_pragma('pragma solidity ^0.5.0;')
        Version('0.5.17')


Importing Already-Installed Versions
====================================

.. py:function:: solcx.import_installed_solc(solcx_binary_path=None)

    Search for and copy installed ``solc`` versions into the local installation folder.

    This function is especially useful on OSX, to access Solidity versions that you have installed from homebrew and where a precompiled binary is not available.

    .. code-block:: python

        >>> solcx.import_installed_solc()
        [Version('0.7.0'), Version('0.6.12')]


Installing Solidity
===================

py-solc-x downloads and installs precompiled binaries from `solc-bin.ethereum.org <solc-bin.ethereum.org>`_. Different binaries are available depending on your operating system.

Getting Installable Versions
----------------------------

.. py:function:: solcx.get_installable_solc_versions()

    Return a list of all ``solc`` versions that can be installed by py-solc-x.


    .. code-block:: python

        >>> solcx.get_installable_solc_versions()
        [Version('0.7.0'), Version('0.6.12'), Version('0.6.11'), Version('0.6.10'), Version('0.6.9'), Version('0.6.8'), Version('0.6.7'), Version('0.6.6'), Version('0.6.5'), Version('0.6.4'), Version('0.6.3'), Version('0.6.2'), Version('0.6.1'), Version('0.6.0'), Version('0.5.17'), Version('0.5.16'), Version('0.5.15'), Version('0.5.14'), Version('0.5.13'), Version('0.5.12'), Version('0.5.11'), Version('0.5.10'), Version('0.5.9'), Version('0.5.8'), Version('0.5.7'), Version('0.5.6'), Version('0.5.5'), Version('0.5.4'), Version('0.5.3'), Version('0.5.2'), Version('0.5.1'), Version('0.5.0'), Version('0.4.26'), Version('0.4.25'), Version('0.4.24'), Version('0.4.23'), Version('0.4.22'), Version('0.4.21'), Version('0.4.20'), Version('0.4.19'), Version('0.4.18'), Version('0.4.17'), Version('0.4.16'), Version('0.4.15'), Version('0.4.14'), Version('0.4.13'), Version('0.4.12'), Version('0.4.11')]

Installing Precompiled Binaries
-------------------------------

.. py:function:: solcx.install_solc(version="latest", show_progress=False, solcx_binary_path=None)

    Download and install a precompiled ``solc`` binary.

        ``version`` str | Version
            Version of ``solc`` to install. Default is the newest available version.
        ``show_progress`` bool
            If ``True``, display a progress bar while downloading. Requires installing
            the `tqdm <https://github.com/tqdm/tqdm>`_ package.
        ``solcx_binary_path`` Path | str
            User-defined path, used to override the default installation directory.

Building from Source
====================

When a precompiled version of Solidity isn't available for your operating system, you may still install it by building from the source code. Source code is downloaded from `Github <https://github.com/ethereum/solidity/releases>`_.

.. note::

    If you wish to compile from source you must first install the required `solc dependencies <https://solidity.readthedocs.io/en/latest/installing-solidity.html#building-from-source>`_.


Getting Compilable Versions
---------------------------

.. py:function:: solcx.get_compilable_solc_versions(headers=None)

    Return a list of all ``solc`` versions that can be installed by py-solc-x.

        ``headers`` Dict
            Headers to include in the request to Github.

    .. code-block:: python

        >>> solcx.get_compilable_solc_versions()
        [Version('0.7.0'), Version('0.6.12'), Version('0.6.11'), Version('0.6.10'), Version('0.6.9'), Version('0.6.8'), Version('0.6.7'), Version('0.6.6'), Version('0.6.5'), Version('0.6.4'), Version('0.6.3'), Version('0.6.2'), Version('0.6.1'), Version('0.6.0'), Version('0.5.17'), Version('0.5.16'), Version('0.5.15'), Version('0.5.14'), Version('0.5.13'), Version('0.5.12'), Version('0.5.11'), Version('0.5.10'), Version('0.5.9'), Version('0.5.8'), Version('0.5.7'), Version('0.5.6'), Version('0.5.5'), Version('0.5.4'), Version('0.5.3'), Version('0.5.2'), Version('0.5.1'), Version('0.5.0'), Version('0.4.26'), Version('0.4.25'), Version('0.4.24'), Version('0.4.23'), Version('0.4.22'), Version('0.4.21'), Version('0.4.20'), Version('0.4.19'), Version('0.4.18'), Version('0.4.17'), Version('0.4.16'), Version('0.4.15'), Version('0.4.14'), Version('0.4.13'), Version('0.4.12'), Version('0.4.11')]


Compiling Solidity from Source
------------------------------

.. py:function:: solcx.compile_solc(version, show_progress=False, solcx_binary_path=None)

    Install a version of ``solc`` by downloading and compiling source code.

    This function is only available when using Linux or OSX.

    **Arguments:**

        ``version`` str | Version
            Version of ``solc`` to install.
        ``show_progress`` bool
            If ``True``, display a progress bar while downloading. Requires installing
            the `tqdm <https://github.com/tqdm/tqdm>`_ package.
        ``solcx_binary_path`` Path | str
            User-defined path, used to override the default installation directory.
