import functools
import json
import re

from semantic_version import Version

from .exceptions import ContractsNotFound, SolcError
from .wrapper import solc_wrapper

VERSION_DEV_DATE_MANGLER_RE = re.compile(r"(\d{4})\.0?(\d{1,2})\.0?(\d{1,2})")
strip_zeroes_from_month_and_day = functools.partial(
    VERSION_DEV_DATE_MANGLER_RE.sub, r"\g<1>.\g<2>.\g<3>"
)


def get_solc_version() -> Version:
    stdoutdata, stderrdata, command, proc = solc_wrapper(version=True)
    if "Version: " not in stdoutdata:
        raise SolcError(
            command=command,
            return_code=proc.returncode,
            stdin_data=None,
            stdout_data=stdoutdata,
            stderr_data=stderrdata,
            message="Unable to extract version string from command output",
        )
    version_string = stdoutdata.split("Version: ", maxsplit=1)[1]
    version_string = version_string.replace("++", "pp").strip()
    return Version(strip_zeroes_from_month_and_day(version_string))


def _get_combined_json_outputs() -> str:
    help_str = solc_wrapper(help=True)[0].split("\n")
    combined_json_args = next(i for i in help_str if i.startswith("  --combined-json"))
    return combined_json_args.split(" ")[-1]


def _parse_compiler_output(stdoutdata) -> dict:
    output = json.loads(stdoutdata)

    contracts = output.get("contracts", {})
    sources = output.get("sources", {})

    for path_str, data in contracts.items():
        if "abi" in data:
            data["abi"] = json.loads(data["abi"])
        key = path_str.rsplit(":", maxsplit=1)[0]
        if "AST" in sources.get(key, {}):
            data["ast"] = sources[key]["AST"]

    return contracts


def compile_source(
    source: str,
    output_values: list = None,
    import_remappings: list = None,
    base_path: str = None,
    allow_paths: list = None,
    output_dir: str = None,
    overwrite: bool = False,
    evm_version: str = None,
    revert_strings: bool = False,
    metadata_hash: str = None,
    metadata_literal: bool = False,
    optimize: bool = False,
    optimize_runs: int = None,
    no_optimize_yul: bool = False,
    yul_optimizations: int = None,
    allow_empty: bool = False,
) -> dict:

    if output_values is None:
        combined_json = _get_combined_json_outputs()
    else:
        combined_json = ",".join(output_values)

    compiler_kwargs = dict(
        stdin=source,
        combined_json=combined_json,
        import_remappings=import_remappings,
        base_path=base_path,
        allow_paths=allow_paths,
        output_dir=output_dir,
        overwrite=overwrite,
        evm_version=evm_version,
        revert_strings=revert_strings,
        metadata_hash=metadata_hash,
        metadata_literal=metadata_literal,
        optimize=optimize,
        optimize_runs=optimize_runs,
        no_optimize_yul=no_optimize_yul,
        yul_optimizations=yul_optimizations,
    )

    stdoutdata, stderrdata, command, proc = solc_wrapper(**compiler_kwargs)

    contracts = _parse_compiler_output(stdoutdata)

    if not contracts and not allow_empty:
        raise ContractsNotFound(
            command=command,
            return_code=proc.returncode,
            stdin_data=source,
            stdout_data=stdoutdata,
            stderr_data=stderrdata,
        )
    return contracts


def compile_files(
    source_files: str,
    output_values: list = None,
    import_remappings: list = None,
    base_path: str = None,
    allow_paths: list = None,
    output_dir: str = None,
    overwrite: bool = False,
    evm_version: str = None,
    revert_strings: bool = False,
    metadata_hash: str = None,
    metadata_literal: bool = False,
    optimize: bool = False,
    optimize_runs: int = None,
    no_optimize_yul: bool = False,
    yul_optimizations: int = None,
    allow_empty: bool = False,
) -> dict:
    if output_values is None:
        combined_json = _get_combined_json_outputs()
    else:
        combined_json = ",".join(output_values)

    compiler_kwargs = dict(
        source_files=source_files,
        combined_json=combined_json,
        import_remappings=import_remappings,
        base_path=base_path,
        allow_paths=allow_paths,
        output_dir=output_dir,
        overwrite=overwrite,
        evm_version=evm_version,
        revert_strings=revert_strings,
        metadata_hash=metadata_hash,
        metadata_literal=metadata_literal,
        optimize=optimize,
        optimize_runs=optimize_runs,
        no_optimize_yul=no_optimize_yul,
        yul_optimizations=yul_optimizations,
    )

    stdoutdata, stderrdata, command, proc = solc_wrapper(**compiler_kwargs)

    contracts = _parse_compiler_output(stdoutdata)

    if not contracts and not allow_empty:
        raise ContractsNotFound(
            command=command,
            return_code=proc.returncode,
            stdin_data=None,
            stdout_data=stdoutdata,
            stderr_data=stderrdata,
        )
    return contracts


def compile_standard(
    input_data,
    base_path: str = None,
    allow_paths: list = None,
    output_dir: str = None,
    overwrite: bool = False,
    allow_empty=False,
):
    if not input_data.get("sources") and not allow_empty:
        raise ContractsNotFound(
            command=None,
            return_code=None,
            stdin_data=json.dumps(input_data, sort_keys=True, indent=2),
            stdout_data=None,
            stderr_data=None,
        )

    compiler_kwargs = dict(
        stdin=json.dumps(input_data),
        standard_json=True,
        base_path=base_path,
        allow_paths=allow_paths,
        output_dir=output_dir,
        overwrite=overwrite,
    )

    stdoutdata, stderrdata, command, proc = solc_wrapper(**compiler_kwargs)

    compiler_output = json.loads(stdoutdata)
    if "errors" in compiler_output:
        has_errors = any(error["severity"] == "error" for error in compiler_output["errors"])
        if has_errors:
            error_message = "\n".join(
                tuple(
                    error["formattedMessage"]
                    for error in compiler_output["errors"]
                    if error["severity"] == "error"
                )
            )
            raise SolcError(
                command,
                proc.returncode,
                json.dumps(input_data),
                stdoutdata,
                stderrdata,
                message=error_message,
            )
    return compiler_output


def link_code(unlinked_bytecode, libraries):
    libraries_arg = ",".join(
        (":".join((lib_name, lib_address)) for lib_name, lib_address in libraries.items())
    )
    stdoutdata, stderrdata, _, _ = solc_wrapper(
        stdin=unlinked_bytecode, link=True, libraries=libraries_arg
    )

    return stdoutdata.replace("Linking completed.", "").strip()
