import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from packaging.version import Version

from solcx import install
from solcx.exceptions import SolcError, UnknownOption, UnknownValue

# (major.minor.patch)(nightly)(commit)
VERSION_REGEX = r"(\d+\.\d+\.\d+)(?:-nightly.\d+.\d+.\d+|)(\+commit.\w+)"


def get_version_str_from_solc_binary(solc_binary: Union[Path, str]) -> str:
    stdout_data = subprocess.check_output([str(solc_binary), "--version"], encoding="utf8")
    if not (match := next(re.finditer(VERSION_REGEX, stdout_data), None)):
        raise SolcError("Could not determine the solc binary version")

    # NOTE: May include "-nightly" suffix.
    return "".join(match.groups())


def get_solc_version(solc_binary: Union[Path, str], with_commit_hash: bool = False) -> Version:
    version_str = get_version_str_from_solc_binary(solc_binary)
    version = Version(version_str.replace("-nightly", ""))
    return version if with_commit_hash else Version(version.base_version)


def _to_string(key: str, value: Any) -> str:
    # convert data into a string prior to calling `solc`
    if isinstance(value, (int, str)):
        return str(value)
    elif isinstance(value, Path):
        return value.as_posix()
    elif isinstance(value, (list, tuple)):
        return ",".join(_to_string(key, i) for i in value)
    else:
        raise TypeError(f"Invalid type for {key}: {type(value)}")


def solc_wrapper(
    solc_binary: Optional[Union[Path, str]] = None,
    stdin: Optional[str] = None,
    source_files: Optional[Union[List, Path, str]] = None,
    import_remappings: Optional[Union[Dict, List, str]] = None,
    success_return_code: Optional[int] = None,
    **kwargs: Any,
) -> Tuple[str, str, List, subprocess.Popen]:
    """
    Wrapper function for calling to ``solc``.

    Args:
      solc_binary (Optional[Union[Path, str]]): Location of the
        ``solc`` binary. If not given, the current default binary is used.
      stdin (Optional[str]): Input to pass to ``solc`` via stdin.
      source_files (Optional[Union[List, Path, str]]): Path, or list of
        paths, of sources to compile
      import_remappings (Optional[Union[Dict, List, str]]): Path remappings.
        May be given as a string or list of strings, formatted as ``"prefix=path"``
        or a dict of ``{"prefix": "path"}``.
      success_return_code (Optional[int]): Expected exit code.
        Raises :class:`~solcx.exceptions.SolcError`` if the process returns a
        different value.
      **kwargs (Any): Flags to be passed to ``solc``. Keywords are converted to
        flags by prepending ``--`` and replacing ``_`` with ``-``, for example the
        keyword ``evm_version`` becomes ``--evm-version``. Values may be given in
        the following formats:

            * ``False``, ``None``: ignored
            * ``True``: flag is used without any arguments
            * str: given as an argument without modification
            * int: given as an argument, converted to a string
            * Path: converted to a string via ``Path.as_posix()``
            * List, Tuple: elements are converted to strings and joined with ``,``

    Returns:
      str: Process ``stdout`` output.
      str: Process ``stderr`` output.
      List: Full command executed by the function.
      Popen: Subprocess object used to call ``solc``.
    """
    solc_binary = Path(solc_binary) if solc_binary else install.get_executable()
    solc_version = get_solc_version(solc_binary)
    command: List = [str(solc_binary)]

    if (
        success_return_code is None
        and ("--help" in command or "help" in kwargs)
        and Version(solc_version.base_version) < Version("0.8.10")
    ):
        success_return_code = 1
    else:
        success_return_code = success_return_code or 0

    if source_files is not None:
        if isinstance(source_files, (str, Path)):
            command.append(_to_string("source_files", source_files))
        else:
            command.extend([_to_string("source_files", i) for i in source_files])

    if import_remappings is not None:
        if isinstance(import_remappings, str):
            command.append(import_remappings)
        else:
            if isinstance(import_remappings, dict):
                import_remappings = [f"{k}={v}" for k, v in import_remappings.items()]
            command.extend(import_remappings)

    for key, value in kwargs.items():
        if value is None or value is False:
            continue

        key = f"--{key.replace('_', '-')}"
        if value is True:
            command.append(key)
        else:
            command.extend([key, _to_string(key, value)])

    if "standard_json" not in kwargs and not source_files:
        # indicates that solc should read from stdin
        command.append("-")

    if stdin is not None:
        stdin = str(stdin)

    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf8",
    )

    stdoutdata, stderrdata = proc.communicate(stdin)

    stderrdata = (
        stderrdata.replace("Error: ", "") if stderrdata.startswith("Error: ") else stderrdata
    )

    if proc.returncode != success_return_code:
        if stderrdata.startswith("unrecognised option"):
            # unrecognised option '<FLAG>'
            flag = stderrdata.split("'")[1]
            raise UnknownOption(
                f"solc {solc_version.base_version} does not support the '{flag}' option'"
            )
        if stderrdata.startswith("Invalid option"):
            # Invalid option to <FLAG>: <OPTION>
            flag, option = stderrdata.split(": ")
            flag = flag.split(" ")[-1]
            raise UnknownValue(
                f"solc {solc_version.base_version} does not accept "
                f"'{option}' as an option for the '{flag}' flag"
            )

        raise SolcError(
            command=command,
            return_code=proc.returncode,
            stdin_data=stdin,
            stdout_data=stdoutdata,
            stderr_data=stderrdata,
        )

    return stdoutdata, stderrdata, command, proc
