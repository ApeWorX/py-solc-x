import subprocess
from pathlib import Path
from typing import Any

from semantic_version import Version

from .exceptions import SolcError
from .install import get_executable


def _to_string(key: str, value: Any) -> str:
    if isinstance(value, (int, str)):
        return str(value)
    elif isinstance(value, Path):
        return value.as_posix()
    elif isinstance(value, (list, tuple)):
        return ",".join(_to_string(key, i) for i in value)
    else:
        raise TypeError(f"Invalid type for {key}: {type(value)}")


def solc_wrapper(
    solc_binary: str = None,
    stdin: str = None,
    source_files: list = None,
    import_remappings: list = None,
    success_return_code: int = None,
    **kwargs: Any,
):
    if solc_binary is None:
        solc_binary = get_executable()

    command = [solc_binary]

    if "help" in kwargs:
        success_return_code = 1
    elif success_return_code is None:
        success_return_code = 0

    if source_files is not None:
        command.extend([_to_string("source_files", i) for i in source_files])

    if import_remappings is not None:
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

    if proc.returncode != success_return_code:
        solc_version = Version(solc_binary.rsplit("-v")[-1].split("\\")[0])
        if stderrdata.startswith("unrecognised option"):
            # unrecognised option '<FLAG>'
            flag = stderrdata.split("'")[1]
            raise AttributeError(f"solc {solc_version} - unsupported flag: {flag}")
        if stderrdata.startswith("Invalid option"):
            # Invalid option to <FLAG>: <OPTION>
            flag, option = stderrdata.split(": ")
            flag = flag.split(" ")[-1]
            raise ValueError(f"solc {solc_version} - invalid option for {flag} flag: {option}")

        raise SolcError(
            command=command,
            return_code=proc.returncode,
            stdin_data=stdin,
            stdout_data=stdoutdata,
            stderr_data=stderrdata,
        )

    return stdoutdata, stderrdata, command, proc
