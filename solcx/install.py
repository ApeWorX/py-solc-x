"""
Install solc
"""
from io import BytesIO
import os
from pathlib import Path
import re
import requests
from semantic_version import Version, Spec
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
        path_list = [
            subprocess.run(['which', 'solc'], stdout=subprocess.PIPE).stdout.decode().strip()
        ]
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


def set_solc_version_pragma(pragma_string, silent=False, check_new=False):
    version = _select_pragma_version(
        pragma_string,
        [Version(i[1:]) for i in get_installed_solc_versions()]
    )
    if not version:
        raise SolcNotInstalled(
            "No compatible solc version installed. " +
            "Use solcx.install_solc_version_pragma('{}') to install.".format(version)
        )
    global solc_version
    solc_version = version
    if not silent:
        print("Using solc version {}".format(solc_version))
    if check_new:
        latest = install_solc_pragma(pragma_string, False)
        if Version(latest) > Version(version):
            print("Newer compatible solc version exists: {}".format(latest))


def install_solc_pragma(pragma_string, install=True):
    version = _select_pragma_version(
        pragma_string,
        [Version(i[1:]) for i in get_available_solc_versions()]
    )
    if not version:
        raise ValueError("Compatible solc version does not exist")
    if install:
        install_solc(version)
    return version


def get_available_solc_versions(headers={}):
    versions = []
    pattern = VERSION_REGEX[_get_platform()]
    for release in requests.get(ALL_RELEASES, headers=headers).json():
        asset = next((i for i in release['assets'] if re.match(pattern, i['name'])), False)
        if asset:
            versions.append(release['tag_name'])
        if release['tag_name'] == MINIMAL_SOLC_VERSION:
            break
    return versions


def _select_pragma_version(pragma_string, version_list):
    comparator_set_range = pragma_string.replace(" ", "").split('||')
    comparator_regex = re.compile(r"(([<>]?=?|\^)\d+\.\d+\.\d+)+")
    version = None

    for comparator_set in comparator_set_range:
        spec = Spec(*(i[0] for i in comparator_regex.findall(comparator_set)))
        selected = spec.select(version_list)
        if selected and (not version or version < selected):
            version = selected
    if version:
        return str(version)


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


def _check_version(version):
    version = Version(version.lstrip('v'))
    if version not in Spec('>=0.4.11'):
        raise ValueError("py-solc-x does not support solc versions <0.4.11")
    return "v" + str(version)


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
