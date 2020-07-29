import json
from pathlib import Path
from typing import Dict, List, Union

from semantic_version import Version

from solcx.exceptions import ContractsNotFound, SolcError
from solcx.install import get_executable
from solcx.wrapper import _get_solc_version, solc_wrapper


def get_solc_version() -> Version:
    solc_binary = get_executable()
    return _get_solc_version(solc_binary)


def _get_combined_json_outputs() -> str:
    help_str = solc_wrapper(help=True)[0].split("\n")
    combined_json_args = next(i for i in help_str if i.startswith("  --combined-json"))
    return combined_json_args.split(" ")[-1]


def _parse_compiler_output(stdoutdata: str) -> Dict:
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
    output_values: List = None,
    import_remappings: Union[Dict, List] = None,
    base_path: str = None,
    allow_paths: List = None,
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
    solc_binary: Union[str, Path] = None,
    solc_version: Version = None,
    allow_empty: bool = False,
) -> Dict:
    if output_values is None:
        combined_json = _get_combined_json_outputs()
    else:
        combined_json = ",".join(output_values)

    if isinstance(import_remappings, dict):
        import_remappings = [f"{k}={v}" for k, v in import_remappings.items()]

    if solc_binary is None:
        solc_binary = get_executable(solc_version)

    stdoutdata, stderrdata, command, proc = solc_wrapper(
        solc_binary=solc_binary,
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
    source_files: List,
    output_values: List = None,
    import_remappings: Union[Dict, List] = None,
    base_path: str = None,
    allow_paths: List = None,
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
    solc_binary: Union[str, Path] = None,
    solc_version: Version = None,
    allow_empty: bool = False,
) -> Dict:
    if output_values is None:
        combined_json = _get_combined_json_outputs()
    else:
        combined_json = ",".join(output_values)

    if isinstance(import_remappings, dict):
        import_remappings = [f"{k}={v}" for k, v in import_remappings.items()]

    if solc_binary is None:
        solc_binary = get_executable(solc_version)

    stdoutdata, stderrdata, command, proc = solc_wrapper(
        solc_binary=solc_binary,
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

    contracts = _parse_compiler_output(stdoutdata)

    if not contracts and not allow_empty:
        raise ContractsNotFound(
            command=command,
            return_code=proc.returncode,
            stdout_data=stdoutdata,
            stderr_data=stderrdata,
        )
    return contracts


def compile_standard(
    input_data: Dict,
    base_path: str = None,
    allow_paths: List = None,
    output_dir: str = None,
    overwrite: bool = False,
    solc_binary: Union[str, Path] = None,
    solc_version: Version = None,
    allow_empty: bool = False,
) -> Dict:
    if not input_data.get("sources") and not allow_empty:
        raise ContractsNotFound(
            "Input JSON does not contain any sources",
            stdin_data=json.dumps(input_data, sort_keys=True, indent=2),
        )

    if solc_binary is None:
        solc_binary = get_executable(solc_version)

    stdoutdata, stderrdata, command, proc = solc_wrapper(
        solc_binary=solc_binary,
        stdin=json.dumps(input_data),
        standard_json=True,
        base_path=base_path,
        allow_paths=allow_paths,
        output_dir=output_dir,
        overwrite=overwrite,
    )

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
                error_message,
                command=command,
                return_code=proc.returncode,
                stdin_data=json.dumps(input_data),
                stdout_data=stdoutdata,
                stderr_data=stderrdata,
                error_dict=compiler_output["errors"],
            )
    return compiler_output


def link_code(
    unlinked_bytecode: str,
    libraries: Dict,
    solc_binary: Union[str, Path] = None,
    solc_version: Version = None,
) -> str:

    if solc_binary is None:
        solc_binary = get_executable(solc_version)

    library_list = [f"{name}:{address}" for name, address in libraries.items()]

    stdoutdata = solc_wrapper(
        solc_binary=solc_binary, stdin=unlinked_bytecode, link=True, libraries=library_list
    )[0]

    return stdoutdata.replace("Linking completed.", "").strip()
