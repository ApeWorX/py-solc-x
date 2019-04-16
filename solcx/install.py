"""
Install solc
"""
from io import BytesIO
import os
from pathlib import Path
import requests
import shutil
import stat
import subprocess
import sys
import tarfile
import zipfile
import re

DOWNLOAD_BASE = "https://github.com/ethereum/solidity/releases/download/{}/{}"
API = "https://api.github.com/repos/ethereum/solidity/releases/latest"
ALL_RELEASES = "https://api.github.com/repos/ethereum/solidity/releases"

solc_version = None


def get_solc_folder():
    path = Path(__file__).parent.joinpath('bin')
    path.mkdir(exist_ok=True)
    return path


def import_installed_solc():
    if sys.platform.startswith('linux'):
        path_list = [subprocess.check_output(['which','solc']).decode().strip()]
        if not path_list[0]:
            return
    elif sys.platform == 'darwin':
        path_list = [str(i) for i in Path('/usr/local/Cellar').glob('solidity*/**/solc')]
    else:
        return
    for path in path_list:
        version = subprocess.check_output([path, '--version']).decode()
        version = "v"+version[version.index("Version: ")+9:version.index('+')]
        if version in get_installed_solc_versions():
            continue
        shutil.copy(path, str(get_solc_folder().joinpath("solc-" + version)))


def get_executable(version=None):
    if not version:
        version = solc_version
    solc_bin = get_solc_folder().joinpath("solc-" + version)
    if sys.platform == "win32":
        return str(solc_bin.joinpath("solc.exe"))
    return str(solc_bin)


def set_solc_version(version=None):
    version = _check_version(version)
    if not Path(get_executable(version)).exists():
        install_solc(version)
    global solc_version
    solc_version = version
    print("Using solc version {}".format(solc_version))

def set_solc_version_pragma(version):
    version = version.strip()
    comparator_set_range = [i.strip() for i in version.split('||')]
    installed_versions = get_installed_solc_versions()
    comparator_regex = re.compile(r'(?P<operator>([<>]?=?|\^))(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))')
    range_flag = False
    set_version = None
    for installed_version in reversed(installed_versions):
        for comparator_set in comparator_set_range:
            comparators = [m.groupdict() for m in comparator_regex.finditer(comparator_set)]
            comparator_set_flag = True
            for comparator in comparators:
                operator = comparator['operator']
                if not _compare_versions(installed_version, comparator['version'], operator):
                    comparator_set_flag = False
            if comparator_set_flag:
                range_flag = True
        if range_flag:
            set_version = installed_version
            newer_version = install_solc_pragma(version, install=False)
            if _compare_versions(set_version, newer_version, '<'):
                print("Newer compatible solc version exists: {}".format(newer_version))
            break
    if not set_version:
        set_version = install_solc_pragma(version)
    global solc_version
    solc_version = set_version
    print("Using solc version {}".format(solc_version))



def get_installed_solc_versions():
    return sorted(i.name[5:] for i in get_solc_folder().glob('solc-v*'))


def install_solc(version=None):
    version = _check_version(version)
    if sys.platform.startswith('linux'):
        _install_solc_linux(version)
    elif sys.platform == 'darwin':
        _install_solc_osx(version)
    elif sys.platform == 'win32':
        _install_solc_windows(version)
    else:
        raise KeyError("Unknown platform: {}".format(sys.platform))
    binary_path = get_executable(version)
    _check_subprocess_call(
        [binary_path, '--version'],
        message="Checking installed executable version @ {}".format(binary_path)
    )
    print("solc {} successfully installed at: {}".format(version, binary_path))

def install_solc_pragma(version, install=True):
    version = version.strip()
    comparator_set_range = [i.strip() for i in version.split('||')]
    comparator_regex = re.compile(r'(?P<operator>([<>]?=?|\^))(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))')
    versions_json = requests.get(ALL_RELEASES).json()
    range_flag = False
    for version_json in versions_json:
        for comparator_set in comparator_set_range:
            comparators = [m.groupdict() for m in comparator_regex.finditer(comparator_set)]
            comparator_set_flag = True
            for comparator in comparators:
                operator = comparator['operator']
                if not _compare_versions(version_json['tag_name'], comparator['version'], operator):
                    comparator_set_flag = False
            if comparator_set_flag:
                range_flag = True
        if range_flag:
            _check_version(version_json['tag_name'])
            if install:
                install_solc(version_json['tag_name'])
            return version_json['tag_name']
    raise ValueError("Compatible solc version does not exist")

def _compare_versions(v1, v2, operator='='):
    v1 = v1.lstrip('v')
    v2 = v2.lstrip('v')
    v1_split = [int(i) for i in v1.split('.')]
    v2_split = [int(i) for i in v2.split('.')]
    if operator == '' or operator == None:
        operator = '='
    if operator == '=':
        if v1_split[0] == v2_split[0] and v1_split[1] == v2_split[1] and v1_split[2] == v2_split[2]:
            return True
    elif operator == '>=':
        if v1_split[0] > v2_split[0] or (v1_split[0] == v2_split[0] and (v1_split[1] > v2_split[1] or (v1_split[1] == v2_split[1] and v1_split[2] >= v2_split[2]))):
            return True
    elif operator == '>':
        if v1_split[0] > v2_split[0] or (v1_split[0] == v2_split[0] and (v1_split[1] > v2_split[1] or (v1_split[1] == v2_split[1] and v1_split[2] > v2_split[2]))):
            return True
    elif operator == '<=':
        if v1_split[0] > v2_split[0] or (v1_split[0] == v2_split[0] and (v1_split[1] > v2_split[1] or (v1_split[1] == v2_split[1] and v1_split[2] <= v2_split[2]))):
            return True
    elif operator == '<':
        if v1_split[0] > v2_split[0] or (v1_split[0] == v2_split[0] and (v1_split[1] > v2_split[1] or (v1_split[1] == v2_split[1] and v1_split[2] < v2_split[2]))):
            return True
    elif operator == '^':
        if v1_split[0] == v2_split[0] and v1_split[1] == v2_split[1] and v1_split[2] >= v2_split[2]:
            return True
    else:
        raise ValueError("operator {} not supported".format(operator))
    return False


def _check_version(version):
    if not version:
        return requests.get(API).json()['tag_name']
    version = "v0." + version.lstrip("v0.")
    if version.count('.') != 2:
        raise ValueError("solc version must be in the format v0.x.x")
    v = [int(i) for i in version[1:].split('.')]
    if v[1] < 4 or (v[1] == 4 and v[2] < 11):
        raise ValueError("py-solc-x does not support solc versions <0.4.11")
    return version


def _check_subprocess_call(command, message=None, verbose=True, **proc_kwargs):
    if message:
        print(message)
    print("Executing: {0}".format(" ".join(command)))

    return subprocess.check_call(
        command,
        stderr=subprocess.STDOUT if verbose else subprocess.DEVNULL,
        **proc_kwargs
    )


def _chmod_plus_x(executable_path):
    executable_path.chmod(executable_path.stat().st_mode | stat.S_IEXEC)


def _wget(url, path):
    try:
        _check_subprocess_call(
            ["wget", url, "-O", str(path)],
            "Downloading solc from {}".format(url)
        )
    except subprocess.CalledProcessError:
        if path.exists():
            path.unlink()
        raise


def _install_solc_linux(version):
    download = DOWNLOAD_BASE.format(version, "solc-static-linux")
    binary_path = get_solc_folder().joinpath("solc-" + version)
    if binary_path.exists():
        print("solc {} already installed at: {}".format(version, binary_path))
        return
    _wget(download, binary_path)
    _chmod_plus_x(binary_path)


def _install_solc_windows(version):
    download = DOWNLOAD_BASE.format(version, "solidity-windows.zip")
    install_folder = get_solc_folder().joinpath("solc-" + version)
    if install_folder.exists():
        print("solc {} already installed at: {}".format(version, install_folder))
        return
    print("Downloading solc {} from {}".format(version, download))
    request = requests.get(download)
    with zipfile.ZipFile(BytesIO(request.content)) as zf:
        zf.extractall(str(install_folder))


def _install_solc_osx(version):
    if "v0.4" in version:
        raise ValueError(
            "Py-solc-x cannot build solc versions 0.4.x on OSX. If you install solc 0.4.x\n"
            "using brew and reload solcx, the installed version will be available.\n\n"
            "See https://github.com/ethereum/homebrew-ethereum for installation instructions.")
    tar_path = get_solc_folder().joinpath("solc-{}.tar.gz".format(version))
    source_folder = get_solc_folder().joinpath("solidity_" + version[1:])
    download = DOWNLOAD_BASE.format(version, "solidity_{}.tar.gz".format(version[1:]))
    binary_path = get_solc_folder().joinpath("solc-" + version)

    if binary_path.exists():
        print("solc {} already installed at: {}".format(version, binary_path))
        return

    _wget(download, tar_path)

    with tarfile.open(str(tar_path), "r") as tar:
        tar.extractall(str(get_solc_folder()))
    tar_path.unlink()

    _check_subprocess_call(
        ["sh", str(source_folder.joinpath('scripts/install_deps.sh'))],
        message="Running dependency installation script `install_deps.sh` @ {}".format(tar_path)
    )

    original_path = os.getcwd()
    source_folder.joinpath('build').mkdir(exist_ok=True)
    os.chdir(str(source_folder.joinpath('build').resolve()))
    try:
        for cmd in (["cmake", ".."], ["make"]):
            _check_subprocess_call(cmd, message="Running {}".format(cmd[0]))
        os.chdir(original_path)
        source_folder.joinpath('build/solc/solc').rename(binary_path)
    except subprocess.CalledProcessError as e:
        raise OSError(
            "{} returned non-zero exit status {}".format(cmd[0], e.returncode) +
            " while attempting to build solc from the source. This is likely " +
            "due to a missing or incorrect version of an external dependency."
        )
    finally:
        os.chdir(original_path)
        shutil.rmtree(str(source_folder))

    _chmod_plus_x(binary_path)


if __name__ == "__main__":
    try:
        version = sys.argv[1]
    except IndexError:
        print("Invocation error.  Should be invoked as `./install_solc.py <release-tag>`")
        sys.exit(1)

    install_solc(version)
