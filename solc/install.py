"""
Install solc
"""
import functools
import os
import stat
import subprocess
import sys
import contextlib

import zipfile


# V0_4_1 = 'v0.4.1'
# V0_4_2 = 'v0.4.2'
# V0_4_6 = 'v0.4.6'
# V0_4_7 = 'v0.4.7'
# V0_4_8 = 'v0.4.8'
# V0_4_9 = 'v0.4.9'
# V0_4_11 = 'v0.4.11'
# V0_4_12 = 'v0.4.12'
# V0_4_13 = 'v0.4.13'
# V0_4_14 = 'v0.4.14'
# V0_4_15 = 'v0.4.15'
# V0_4_16 = 'v0.4.16'
# V0_4_17 = 'v0.4.17'
# V0_4_18 = 'v0.4.18'
# V0_4_19 = 'v0.4.19'
# V0_4_20 = 'v0.4.20'
# V0_4_21 = 'v0.4.21'
# V0_4_22 = 'v0.4.22'
# V0_4_23 = 'v0.4.23'
# V0_4_24 = 'v0.4.24'
# V0_4_25 = 'v0.4.25'
# V0_5_0 = 'v0.5.0'
# V0_5_1 = 'v0.5.1'
# V0_5_2 = 'v0.5.2'

#
# System utilities.
#
# @contextlib.contextmanager
# def chdir(path):
#     original_path = os.getcwd()
#     try:
#         os.chdir(path)
#         yield
#     finally:
#         os.chdir(original_path)


# def is_executable_available(program):
#     def is_exe(fpath):
#         return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

#     fpath = os.path.dirname(program)
#     if fpath:
#         if is_exe(program):
#             return True
#     else:
#         for path in os.environ["PATH"].split(os.pathsep):
#             path = path.strip('"')
#             exe_file = os.path.join(path, program)
#             if is_exe(exe_file):
#                 return True

#     return False


# def ensure_path_exists(dir_path):
#     """
#     Make sure that a path exists
#     """
#     if not os.path.exists(dir_path):
#         os.makedirs(dir_path)
#         return True
#     return False


# def ensure_parent_dir_exists(path):
#     ensure_path_exists(os.path.dirname(path))


# def check_subprocess_call(command, message=None, stderr=subprocess.STDOUT, **proc_kwargs):
#     if message:
#         print(message)
#     print("Executing: {0}".format(" ".join(command)))

#     return subprocess.check_call(
#         command,
#         stderr=subprocess.STDOUT,
#         **proc_kwargs
#     )







# SOLIDITY_GIT_URI = "https://github.com/ethereum/solidity.git"


# def is_git_repository(path):
#     git_dir = os.path.join(
#         path,
#         '.git',
#     )
#     return os.path.exists(git_dir)


# #
# #  Installation filesystem path utilities
# #
# def get_base_install_path(identifier):
#     if 'SOLC_BASE_INSTALL_PATH' in os.environ:
#         return os.path.join(
#             os.environ['SOLC_BASE_INSTALL_PATH'],
#             'solc-{0}'.format(identifier),
#         )
#     else:
#         return os.path.expanduser(os.path.join(
#             '~',
#             '.py-solc',
#             'solc-{0}'.format(identifier),
#         ))


# def get_repository_path(identifier):
#     return os.path.join(
#         get_base_install_path(identifier),
#         'source',
#     )



# def get_executable_path(identifier):
#     return __file__.rsplit('/', maxsplit=2)[0] + '/bin/solc-' + identifier


# def get_build_dir(identifier):
#     repository_path = get_repository_path(identifier)
#     return os.path.join(
#         repository_path,
#         'build',
#     )


# def get_built_executable_path(identifier):
#     build_dir = get_build_dir(identifier)
#     return os.path.join(
#         build_dir,
#         'solc',
#         'solc',
#     )


# #
# # Installation primitives.
# #
# def clone_solidity_repository(identifier):
#     if not is_executable_available('git'):
#         raise OSError("The `git` is required but was not found")

#     repository_path = get_repository_path(identifier)
#     ensure_parent_dir_exists(repository_path)
#     command = [
#         "git", "clone",
#         "--recurse-submodules",
#         "--branch", identifier,
#         "--depth", "10",
#         SOLIDITY_GIT_URI,
#         repository_path,
#     ]

#     return check_subprocess_call(
#         command,
#         message="Checking out solidity repository @ {0}".format(identifier),
#     )


# def install_solc_dependencies(identifier):
#     repository_path = get_repository_path(identifier)
#     if not is_git_repository(repository_path):
#         raise OSError("Git repository not found @ {0}".format(repository_path))

#     with chdir(repository_path):
#         install_deps_script_path = os.path.join(repository_path, 'scripts', 'install_deps.sh')

#         return check_subprocess_call(
#             command=["sh", install_deps_script_path],
#             message="Running dependency installation script `install_deps.sh` @ {0}".format(
#                 install_deps_script_path,
#             ),
#         )



SOLC_BASE = __file__[:__file__.rindex('/')] + "/bin/solc-{}"
DOWNLOAD_BASE = "https://github.com/ethereum/solidity/releases/download/{}/{}"



def _check_subprocess_output(command, message=None, stderr=subprocess.STDOUT, **proc_kwargs):
    if message:
        print(message)
    print("Executing: {0}".format(" ".join(command)))

    return subprocess.check_output(
        command,
        stderr=subprocess.STDOUT,
        **proc_kwargs
    )

def _chmod_plus_x(executable_path):
    current_st = os.stat(executable_path)
    os.chmod(executable_path, current_st.st_mode | stat.S_IEXEC)

def install_solc_from_static_linux(identifier):
    download = DOWNLOAD_BASE.format(identifier, "solc-static-linux")
    binary_path = SOLC_BASE.format(identifier)
    
    command = [
        "wget", download,
        '-c',  # resume previously incomplete download.
        '-O', binary_path,
    ]

    _check_subprocess_output(
        command,
        message="Downloading static linux binary from {0}".format(download),
    )

    _chmod_plus_x(binary_path)

    check_subprocess_output(
        [executable_path, '--version'],
        message="Checking installed executable version @ {0}".format(executable_path),
    )

    print("solc successfully installed at: {0}".format(executable_path))


# def build_solc_from_source(identifier):
#     if not is_git_repository(get_repository_path(identifier)):
#         clone_solidity_repository(identifier)

#     build_dir = get_build_dir(identifier)
#     ensure_path_exists(build_dir)

#     with chdir(build_dir):
#         cmake_command = ["cmake", ".."]
#         check_subprocess_call(
#             cmake_command,
#             message="Running cmake build command",
#         )
#         make_command = ["make"]
#         check_subprocess_call(
#             make_command,
#             message="Running make command",
#         )

#     built_executable_path = get_built_executable_path(identifier)
#     chmod_plus_x(built_executable_path)

#     executable_path = get_executable_path(identifier)
#     ensure_parent_dir_exists(executable_path)
#     os.symlink(built_executable_path, executable_path)
#     chmod_plus_x(executable_path)


# def install_from_source(identifier):
#     if not is_git_repository(get_repository_path(identifier)):
#         clone_solidity_repository(identifier)
#     install_solc_dependencies(identifier)
#     build_solc_from_source(identifier)

#     executable_path = get_executable_path(identifier)
#     print("Succesfully installed solc @ `{0}`".format(executable_path))



def install_solc(identifier):
    identifier = "v0." + identifier.lstrip("v0.")
    if not os.path.exists(__file__[:__file__.rindex('/')] + "/bin"):
        os.mkdir(__file__[:__file__.rindex('/')] + "/bin")
    if sys.platform.startswith('linux'):
        return install_solc_from_static_linux(identifier)
    elif sys.platform == 'darwin'
        return install_from_source(identifier)
    elif sys.platform == 'win32':
        return ##
    raise KeyError("Unknown platform: {}".format(sys.platform))


if __name__ == "__main__":
    try:
        identifier = sys.argv[1]
    except IndexError:
        print("Invocation error.  Should be invoked as `./install_solc.py <release-tag>`")
        sys.exit(1)

    install_solc(identifier)
