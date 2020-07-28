import subprocess
from pathlib import Path
from typing import Any, List, Tuple, Union

from semantic_version import Version

from solcx import install
from solcx.exceptions import SolcError


def _get_solc_version(solc_binary: Union[Path, str]) -> Version:
    stdout_data = subprocess.check_output([solc_binary, "--version"], encoding="utf8").strip()
    stdout_data = stdout_data[stdout_data.index("Version: ") + 9 : stdout_data.index("+")]
    return Version.coerce(stdout_data)


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
    solc_binary: Union[Path, str] = None,
    stdin: str = None,
    source_files: list = None,
    import_remappings: list = None,
    success_return_code: int = None,
    **kwargs: Any,
) -> Tuple[str, str, list, subprocess.Popen]:
    if solc_binary:
        solc_binary = Path(solc_binary)
    else:
        solc_binary = install.get_executable()

    solc_version = _get_solc_version(solc_binary)
    command: List = [solc_binary]

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
