from __future__ import absolute_import

import subprocess

from semantic_version import Version

from .exceptions import SolcError
from .install import get_executable
from .utils.string import coerce_return_to_text, force_bytes


@coerce_return_to_text
def solc_wrapper(
    solc_binary=None,
    stdin=None,
    help=None,
    version=None,
    add_std=None,
    combined_json=None,
    optimize=None,
    optimize_runs=None,
    libraries=None,
    output_dir=None,
    gas=None,
    assemble=None,
    link=None,
    source_files=None,
    import_remappings=None,
    ast=None,
    ast_json=None,
    asm=None,
    asm_json=None,
    opcodes=None,
    bin=None,
    bin_runtime=None,
    clone_bin=None,
    abi=None,
    hashes=None,
    userdoc=None,
    devdoc=None,
    formal=None,
    allow_paths=None,
    standard_json=None,
    success_return_code=0,
    evm_version=None,
):
    if solc_binary is None:
        solc_binary = get_executable()

    command = [solc_binary]

    solc_minor = Version(solc_binary.rsplit("-v")[-1].split("\\")[0]).minor

    if help:
        command.append("--help")

    if version:
        command.append("--version")

    # removed in 0.4.21 and does nothing since <0.4.11, should be removed in the future
    if add_std:
        command.append("--add-std")

    if optimize:
        command.append("--optimize")

    if optimize_runs is not None:
        command.extend(("--optimize-runs", str(optimize_runs)))

    if link:
        command.append("--link")

    if libraries is not None:
        command.extend(("--libraries", libraries))

    if output_dir is not None:
        command.extend(("--output-dir", output_dir))

    if combined_json:
        if solc_minor >= 5:
            combined_json = combined_json.replace(",clone-bin", "")
        command.extend(("--combined-json", combined_json))

    if gas:
        command.append("--gas")

    if allow_paths:
        command.extend(("--allow-paths", allow_paths))

    if standard_json:
        command.append("--standard-json")

    if assemble:
        command.append("--assemble")

    if import_remappings is not None:
        command.extend(import_remappings)

    if source_files is not None:
        command.extend(source_files)

    # Output configuration
    if ast_json:
        command.append("--ast-json")

    if asm:
        command.append("--asm")

    if asm_json:
        command.append("--asm-json")

    if opcodes:
        command.append("--opcodes")

    if bin:
        command.append("--bin")

    if bin_runtime:
        command.append("--bin-runtime")

    if abi:
        command.append("--abi")

    if hashes:
        command.append("--hashes")

    if userdoc:
        command.append("--userdoc")

    if devdoc:
        command.append("--devdoc")

    if evm_version:
        command.extend(("--evm-version", evm_version))

    # unsupported by >=0.6.0
    if ast:
        if solc_minor >= 6:
            raise AttributeError("solc 0.{}.x does not support the --ast flag".format(solc_minor))
        command.append("--ast")

    # unsupported by >=0.5.0
    if clone_bin:
        if solc_minor >= 5:
            raise AttributeError(
                "solc 0.{}.x does not support the --clone-bin flag".format(solc_minor)
            )
        command.append("--clone-bin")

    if formal:
        if solc_minor >= 5:
            raise AttributeError(
                "solc 0.{}.x does not support the --formal flag".format(solc_minor)
            )
        command.append("--formal")

    if not standard_json and not source_files and solc_minor >= 5:
        command.append("-")

    if stdin is not None:
        # solc seems to expects utf-8 from stdin:
        # see Scanner class in Solidity source
        stdin = force_bytes(stdin, "utf8")

    proc = subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    stdoutdata, stderrdata = proc.communicate(stdin)

    if proc.returncode != success_return_code:
        raise SolcError(
            command=command,
            return_code=proc.returncode,
            stdin_data=stdin,
            stdout_data=stdoutdata,
            stderr_data=stderrdata,
        )

    return stdoutdata, stderrdata, command, proc
