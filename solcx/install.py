"""
Install solc
"""
from io import BytesIO
import operator
import os
from pathlib import Path
import re
import requests
import shutil
import stat
import subprocess
import sys
import tarfile
import zipfile

from .exceptions import SolcNotInstalled

DOWNLOAD_BASE = "https://github.com/ethereum/solidity/releases/download/{}/{}"
ALL_RELEASES = "https://api.github.com/repos/ethereum/solidity/releases"

MINIMAL_SOLC_VERSION = "v0.4.11"
VERSION_REGEX = {
    'darwin': "solidity_[0-9].[0-9].[0-9]{1,}.tar.gz",
    'linux': "solc-static-linux",
    'win32': "solidity-windows.zip"
}

solc_version = None


def _get_platform():
    if sys.platform.startswith('linux'):
        return "linux"
    if sys.platform in ('darwin', 'win32'):
        return sys.platform
    raise KeyError(
        "Unknown platform: '{}' - py-solc-x supports"
        " Linux, OSX and Windows".format(sys.platform)
    )


def get_solc_folder():
    path = Path(__file__).parent.joinpath('bin')
    path.mkdir(exist_ok=True)
    return path


def _import_version(path):
    version = subprocess.check_output([path, '--version']).decode()
    return "v" + version[version.index("Version: ")+9:version.index('+')]


def import_installed_solc():
    platform = _get_platform()
    if platform == 'linux':
        # on Linux, copy active version of solc
        path_list = [subprocess.run(['which', 'solc'], stdout=subprocess.PIPE).stdout.decode().strip()]
        if not path_list[0]:
            return
    elif platform == 'darwin':
        # on OSX, copy all versions of solc from cellar
        path_list = [str(i) for i in Path('/usr/local/Cellar').glob('solidity*/**/solc')]
    else:
        # on Windows, do nothing
        return
    for path in path_list:
        try:
            version = _import_version(path)
            assert version not in get_installed_solc_versions()
        except Exception:
            continue
        copy_path = str(get_solc_folder().joinpath("solc-" + version))
        shutil.copy(path, copy_path)
        try:
            # confirm that solc still works after being copied
            assert version == _import_version(copy_path)
        except Exception:
            os.unlink(copy_path)


def get_executable(version=None):
    if not version:
        version = solc_version
    if not version:
        raise SolcNotInstalled(
            "Solc is not installed. Call solcx.get_available_solc_versions()"
            " to view for available versions and solcx.install_solc() to install."
        )
    solc_bin = get_solc_folder().joinpath("solc-" + version)
    if sys.platform == "win32":
        solc_bin = solc_bin.joinpath("solc.exe")
    if not solc_bin.exists():
        raise SolcNotInstalled(
            "solc {} has not been installed. ".format(version) +
            "Use solcx.install_solc('{}') to install.".format(version)
        )
    return str(solc_bin)


def set_solc_version(version, silent=False):
    version = _check_version(version)
    get_executable(version)
    global solc_version
    solc_version = version
    if not silent:
        print("Using solc version {}".format(solc_version))


def set_solc_version_pragma(version, silent=False):
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
            if not silent and _compare_versions(set_version, newer_version, '<'):
                print("Newer compatible solc version exists: {}".format(newer_version))
            break
    if not set_version:
        set_version = install_solc_pragma(version)
    global solc_version
    solc_version = set_version
    if not silent:
        print("Using solc version {}".format(solc_version))


def get_available_solc_versions():
    versions = []
    pattern = VERSION_REGEX[_get_platform()]
    for release in requests.get(ALL_RELEASES).json():
        asset = next((i for i in release['assets'] if re.match(pattern, i['name'])), False)
        if asset:
            versions.append(release['tag_name'])
        if release['tag_name'] == MINIMAL_SOLC_VERSION:
            break
    return versions


def get_installed_solc_versions():
    return sorted(i.name[5:] for i in get_solc_folder().glob('solc-v*'))


def install_solc(version, allow_osx=False):
    version = _check_version(version)
    platform = _get_platform()
    if platform == 'linux':
        _install_solc_linux(version)
    elif platform == 'darwin':
        _install_solc_osx(version, allow_osx)
    elif platform == 'win32':
        _install_solc_windows(version)
    binary_path = get_executable(version)
    _check_subprocess_call(
        [binary_path, '--version'],
        message="Checking installed executable version @ {}".format(binary_path)
    )
    if not solc_version:
        set_solc_version(version)
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


operator_map = {
    '<': operator.lt,
    '<=': operator.le,
    '>=': operator.ge,
    '>': operator.gt,
    '^': operator.ge
}


def _compare_versions(v1, v2, comp='='):
    v1 = v1.lstrip('v')
    v2 = v2.lstrip('v')
    v1_split = [int(i) for i in v1.split('.')]
    v2_split = [int(i) for i in v2.split('.')]
    if comp in ('=', '==', '', None):
        return v1_split == v2_split
    if comp not in operator_map:
        raise ValueError("operator {} not supported".format(comp))
    idx = next((i for i in range(3) if v1_split[i] != v2_split[i]), 2)
    if comp == '^' and idx != 2:
        return False
    return operator_map[comp](v1_split[idx], v2_split[idx])


def _check_version(version):
    version = "v0." + version.lstrip("v0.")
    if version.count('.') != 2:
        raise ValueError("Invalid solc version '{}' - must be in the format v0.x.x".format(version))
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


def _check_for_installed_version(version):
    path = get_solc_folder().joinpath("solc-" + version)
    if path.exists():
        print("solc {} already installed at: {}".format(version, path))
        return False
    return path


def _get_temp_folder():
    path = Path(__file__).parent.joinpath('temp')
    if path.exists():
        shutil.rmtree(str(path))
    path.mkdir()
    return path


def _install_solc_linux(version):
    download = DOWNLOAD_BASE.format(version, "solc-static-linux")
    binary_path = _check_for_installed_version(version)
    if binary_path:
        temp_path = _get_temp_folder().joinpath("solc-binary")
        _wget(download, temp_path)
        temp_path.rename(binary_path)
        _chmod_plus_x(binary_path)


def _install_solc_windows(version):
    download = DOWNLOAD_BASE.format(version, "solidity-windows.zip")
    install_folder = _check_for_installed_version(version)
    if install_folder:
        temp_path = _get_temp_folder()
        print("Downloading solc {} from {}".format(version, download))
        request = requests.get(download)
        with zipfile.ZipFile(BytesIO(request.content)) as zf:
            zf.extractall(str(temp_path))
        install_folder = get_solc_folder().joinpath("solc-" + version)
        temp_path.rename(install_folder)


def _install_solc_osx(version, allow):
    if version.startswith("v0.4") and not allow:
        raise ValueError(
            "Py-solc-x cannot build solc versions 0.4.x on OSX. If you install solc 0.4.x "
            "using brew and reload solcx, the installed version will be available. "
            "See https://github.com/ethereum/homebrew-ethereum for installation instructions.\n\n"
            "To ignore this error, include 'allow_osx=True' when calling solcx.install_solc()"
        )
    temp_path = _get_temp_folder().joinpath("solc-source.tar.gz".format(version))
    source_folder = _get_temp_folder().joinpath("solidity_" + version[1:])
    download = DOWNLOAD_BASE.format(version, "solidity_{}.tar.gz".format(version[1:]))
    binary_path = _check_for_installed_version(version)
    if not binary_path:
        return

    _wget(download, temp_path)
    with tarfile.open(str(temp_path), "r") as tar:
        tar.extractall(str(_get_temp_folder()))

    _check_subprocess_call(
        ["sh", str(source_folder.joinpath('scripts/install_deps.sh'))],
        message="Running dependency installation script `install_deps.sh` @ {}".format(temp_path)
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
        shutil.rmtree(str(temp_path.parent))

    _chmod_plus_x(binary_path)


if __name__ == "__main__":
    try:
        version = sys.argv[1]
    except IndexError:
        print("Invocation error.  Should be invoked as `./install_solc.py <release-tag>`")
        sys.exit(1)

    install_solc(version)
