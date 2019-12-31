"""
Install solc
"""
from base64 import b64encode
from io import BytesIO
import os
from pathlib import Path
import re
import requests
from semantic_version import Version, SimpleSpec
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import zipfile
import logging

from .exceptions import (
    DownloadError,
    SolcNotInstalled,
)
from .utils.lock import (
    get_process_lock
)

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


DOWNLOAD_BASE = "https://github.com/ethereum/solidity/releases/download/{}/{}"
ALL_RELEASES = "https://api.github.com/repos/ethereum/solidity/releases?per_page=100"

MINIMAL_SOLC_VERSION = "v0.4.11"
VERSION_REGEX = {
    'darwin': "solidity_[0-9].[0-9].[0-9]{1,}.tar.gz",
    'linux': "solc-static-linux",
    'win32': "solidity-windows.zip"
}
LOGGER = logging.getLogger("solcx")

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
    path = Path.home().joinpath('.solcx')
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
        LOGGER.info("Using solc version {}".format(solc_version))


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
        LOGGER.info("Using solc version {}".format(solc_version))
    if check_new:
        latest = install_solc_pragma(pragma_string, False)
        if Version(latest) > Version(version):
            LOGGER.info("Newer compatible solc version exists: {}".format(latest))


def install_solc_pragma(pragma_string, install=True, show_progress=False):
    version = _select_pragma_version(
        pragma_string,
        [Version(i[1:]) for i in get_available_solc_versions()]
    )
    if not version:
        raise ValueError("Compatible solc version does not exist")
    if install:
        install_solc(version, show_progress=show_progress)
    return version


def get_available_solc_versions(headers=None):
    versions = []
    pattern = VERSION_REGEX[_get_platform()]

    # Github sometimes blocks CI from calling their API, if you are having issues try
    # saving an API token to the environment variable GITHUB_TOKEN in your build environment
    # https://github.blog/2013-05-16-personal-api-tokens/
    if not headers and os.getenv('GITHUB_TOKEN'):
        auth = b64encode(os.getenv('GITHUB_TOKEN').encode()).decode()
        headers = {'Authorization': "Basic {}".format(auth)}

    data = requests.get(ALL_RELEASES, headers=headers)
    if data.status_code != 200:
        raise ConnectionError(
            "Status {} when getting solc versions from Github: '{}'".format(
                data.status_code,
                data.json()['message']
            )
        )

    for release in data.json():
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
        spec = SimpleSpec(*(i[0] for i in comparator_regex.findall(comparator_set)))
        selected = spec.select(version_list)
        if selected and (not version or version < selected):
            version = selected
    if version:
        return str(version)


def get_installed_solc_versions():
    return sorted(i.name[5:] for i in get_solc_folder().glob('solc-v*'))


def install_solc(version, allow_osx=False, show_progress=False):
    platform = _get_platform()
    version = _check_version(version)

    lock = get_process_lock(version)
    if not lock.acquire(False):
        lock.wait()
        if not _check_for_installed_version(version):
            return
        return install_solc(version, allow_osx)

    try:
        if platform == 'linux':
            _install_solc_linux(version, show_progress)
        elif platform == 'darwin':
            _install_solc_osx(version, allow_osx, show_progress)
        elif platform == 'win32':
            _install_solc_windows(version, show_progress)
        binary_path = get_executable(version)
        _check_subprocess_call(
            [binary_path, '--version'],
            message="Checking installed executable version @ {}".format(binary_path)
        )
        if not solc_version:
            set_solc_version(version)
        LOGGER.info("solc {} successfully installed at: {}".format(version, binary_path))
    finally:
        lock.release()


def _check_version(version):
    version = Version(version.lstrip('v'))
    if version not in SimpleSpec('>=0.4.11'):
        raise ValueError("py-solc-x does not support solc versions <0.4.11")
    return "v" + str(version)


def _check_subprocess_call(command, message=None, verbose=False, **proc_kwargs):
    if message:
        LOGGER.debug(message)
    LOGGER.info("Executing: {0}".format(" ".join(command)))

    return subprocess.check_call(
        command,
        stderr=subprocess.STDOUT if verbose else subprocess.DEVNULL,
        **proc_kwargs
    )


def _chmod_plus_x(executable_path):
    executable_path.chmod(executable_path.stat().st_mode | stat.S_IEXEC)


def _check_for_installed_version(version):
    path = get_solc_folder().joinpath("solc-" + version)
    if path.exists():
        LOGGER.info("solc {} already installed at: {}".format(version, path))
        return False
    return path


def _get_temp_folder():
    path = Path(tempfile.gettempdir()).joinpath('py-solc-x-tmp')
    if path.exists():
        shutil.rmtree(str(path))
    path.mkdir()
    return path


def _download_solc(url, show_progress):
    if not show_progress:
        response = requests.get(url)
        content = response.content
    else:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
        content = bytes()

        for data in response.iter_content(1024, decode_unicode=True):
            progress_bar.update(len(data))
            content += data
        progress_bar.close()

    if response.status_code != 200:
        raise DownloadError(
            "Received status code {} when attempting to download from {}".format(
                response.status_code,
                url
            )
        )
    return content


def _install_solc_linux(version, show_progress):
    download = DOWNLOAD_BASE.format(version, "solc-static-linux")
    binary_path = _check_for_installed_version(version)
    if binary_path:
        LOGGER.info("Downloading solc {} from {}".format(version, download))
        content = _download_solc(download, show_progress)
        with open(binary_path, 'wb') as fp:
            fp.write(content)
        _chmod_plus_x(binary_path)


def _install_solc_windows(version, show_progress):
    download = DOWNLOAD_BASE.format(version, "solidity-windows.zip")
    install_folder = _check_for_installed_version(version)
    if install_folder:
        temp_path = _get_temp_folder()
        content = _download_solc(download, show_progress)
        with zipfile.ZipFile(BytesIO(content)) as zf:
            zf.extractall(str(temp_path))
        install_folder = get_solc_folder().joinpath("solc-" + version)
        temp_path.rename(install_folder)


def _install_solc_osx(version, allow_osx, show_progress):
    if version.startswith("v0.4") and not allow_osx:
        raise ValueError(
            "Py-solc-x cannot build solc versions 0.4.x on OSX. If you install solc 0.4.x "
            "using brew and reload solcx, the installed version will be available. "
            "See https://github.com/ethereum/homebrew-ethereum for installation instructions.\n\n"
            "To ignore this error, include 'allow_osx=True' when calling solcx.install_solc()"
        )
    temp_path = _get_temp_folder()
    download = DOWNLOAD_BASE.format(version, "solidity_{}.tar.gz".format(version[1:]))
    binary_path = _check_for_installed_version(version)
    if not binary_path:
        return

    content = _download_solc(download, show_progress)
    with tarfile.open(fileobj=BytesIO(content)) as tar:
        tar.extractall(temp_path)
    temp_path = temp_path.joinpath('solidity_{}'.format(version[1:]))

    try:
        _check_subprocess_call(
            ["sh", str(temp_path.joinpath('scripts/install_deps.sh'))],
            message="Running dependency installation script `install_deps.sh`"
        )
    except subprocess.CalledProcessError as e:
        LOGGER.warning(e, exc_info=True)

    original_path = os.getcwd()
    temp_path.joinpath('build').mkdir(exist_ok=True)
    os.chdir(str(temp_path.joinpath('build').resolve()))
    try:
        for cmd in (["cmake", ".."], ["make"]):
            _check_subprocess_call(cmd, message="Running {}".format(cmd[0]))
        temp_path.joinpath('build/solc/solc').rename(binary_path)
    except subprocess.CalledProcessError as e:
        raise OSError(
            "{} returned non-zero exit status {} while attempting to build solc from the source. "
            "This is likely due to a missing or incorrect version of an external dependency.\n\n"
            "You may be able to solve this by installing the specific version using brew: "
            "https://solidity.readthedocs.io/en/v0.6.0/installing-solidity.html#binary-packages"
            "".format(cmd[0], e.returncode)
        )
    finally:
        os.chdir(original_path)

    _chmod_plus_x(binary_path)


if __name__ == "__main__":
    try:
        version = sys.argv[1]
    except IndexError:
        LOGGER.error("Invocation error.  Should be invoked as `./install_solc.py <release-tag>`")
        sys.exit(1)

    install_solc(version)
