"""
Install solc
"""
import argparse
import logging
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from base64 import b64encode
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Union

import requests
from semantic_version import SimpleSpec, Version

from .exceptions import DownloadError, SolcNotInstalled
from .utils.lock import get_process_lock

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


DOWNLOAD_BASE = "https://github.com/ethereum/solidity/releases/download/v{}/{}"
ALL_RELEASES = "https://api.github.com/repos/ethereum/solidity/releases?per_page=100"

MINIMAL_SOLC_VERSION = "v0.4.11"
VERSION_REGEX = {
    "darwin": "solidity_[0-9].[0-9].[0-9]{1,}.tar.gz",
    "linux": "solc-static-linux",
    "win32": "solidity-windows.zip",
}
LOGGER = logging.getLogger("solcx")

SOLCX_BINARY_PATH_VARIABLE = "SOLCX_BINARY_PATH"

solc_version = None


def _get_arch() -> str:
    if platform.machine().startswith("arm") or platform.machine() == "aarch64":
        return "arm"
    if platform.machine().startswith("x86"):
        return "x86"
    else:
        return platform.machine()


def _get_platform() -> str:
    if sys.platform.startswith("linux"):
        return "linux"
    if sys.platform in ("darwin", "win32"):
        return sys.platform
    raise KeyError(
        f"Unknown platform: '{sys.platform}' - py-solc-x supports Linux, OSX and Windows"
    )


def _convert_and_validate_version(version: Union[str, Version]) -> Version:
    # take a user-supplied version as a string or Version
    # validate the value, and return a Version object
    if not isinstance(version, Version):
        version = Version(version.lstrip("v"))
    if version not in SimpleSpec(">=0.4.11"):
        raise ValueError("py-solc-x does not support solc versions <0.4.11")
    return version


def get_solc_folder(solcx_binary_path: Union[Path, str] = None) -> Path:
    if os.getenv(SOLCX_BINARY_PATH_VARIABLE):
        return Path(os.environ[SOLCX_BINARY_PATH_VARIABLE])
    elif solcx_binary_path is not None:
        return Path(solcx_binary_path)
    else:
        path = Path.home().joinpath(".solcx")
        path.mkdir(exist_ok=True)
        return path


def _get_import_version(path: str) -> Version:
    stdout_data = subprocess.check_output([path, "--version"]).decode().strip()
    stdout_data = stdout_data[stdout_data.index("Version: ") + 9 : stdout_data.index("+")]
    return Version.coerce(stdout_data)


def import_installed_solc(solcx_binary_path: Union[Path, str] = None) -> None:
    platform = _get_platform()
    if platform == "win32":
        return

    # copy active version of solc
    path_list = []
    which = (
        subprocess.run(["which", "solc"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        .stdout.decode()
        .strip()
    )
    if which:
        path_list.append(which)

    # on OSX, also copy all versions of solc from cellar
    if platform == "darwin":
        path_list = [str(i) for i in Path("/usr/local/Cellar").glob("solidity*/**/solc")]

    for path in path_list:
        try:
            version = _get_import_version(path)
            assert version not in get_installed_solc_versions()
        except Exception:
            continue
        copy_path = str(get_solc_folder(solcx_binary_path).joinpath(f"solc-v{version}"))
        shutil.copy(path, copy_path)
        try:
            # confirm that solc still works after being copied
            assert version == _get_import_version(copy_path)
        except Exception:
            os.unlink(copy_path)


def get_executable(
    version: Union[str, Version] = None, solcx_binary_path: Union[Path, str] = None
) -> Path:
    if not version:
        version = solc_version
    else:
        version = _convert_and_validate_version(version)
    if not version:
        raise SolcNotInstalled(
            "Solc is not installed. Call solcx.get_available_solc_versions()"
            " to view for available versions and solcx.install_solc() to install."
        )
    solc_bin = get_solc_folder(solcx_binary_path).joinpath(f"solc-v{version}")
    if sys.platform == "win32":
        solc_bin = solc_bin.joinpath("solc.exe")
    if not solc_bin.exists():
        raise SolcNotInstalled(
            f"solc {version} has not been installed."
            f" Use solcx.install_solc('{version}') to install."
        )
    return solc_bin


def set_solc_version(
    version: Union[str, Version], silent: bool = False, solcx_binary_path: Union[Path, str] = None
) -> None:
    version = _convert_and_validate_version(version)
    get_executable(version, solcx_binary_path)
    global solc_version
    solc_version = version
    if not silent:
        LOGGER.info(f"Using solc version {solc_version}")


def set_solc_version_pragma(pragma_string, silent=False, check_new=False):
    version = _select_pragma_version(pragma_string, get_installed_solc_versions())
    if not version:
        raise SolcNotInstalled(
            f"No compatible solc version installed."
            f" Use solcx.install_solc_version_pragma('{version}') to install."
        )
    version = _convert_and_validate_version(version)
    global solc_version
    solc_version = version
    if not silent:
        LOGGER.info(f"Using solc version {solc_version}")
    if check_new:
        latest = install_solc_pragma(pragma_string, False)
        if latest > version:
            LOGGER.info(f"Newer compatible solc version exists: {latest}")


def install_solc_pragma(
    pragma_string: str,
    install: bool = True,
    show_progress: bool = False,
    solcx_binary_path: Union[Path, str] = None,
) -> Version:
    version = _select_pragma_version(pragma_string, get_available_solc_versions())
    if not version:
        raise ValueError("Compatible solc version does not exist")
    if install:
        install_solc(version, show_progress=show_progress, solcx_binary_path=solcx_binary_path)
    return version


def get_available_solc_versions(headers: Optional[Dict] = None) -> List[Version]:
    version_list = []
    pattern = VERSION_REGEX[_get_platform()]

    if headers is None and os.getenv("GITHUB_TOKEN") is not None:
        auth = b64encode(os.environ["GITHUB_TOKEN"].encode()).decode()
        headers = {"Authorization": f"Basic {auth}"}

    data = requests.get(ALL_RELEASES, headers=headers)
    if data.status_code != 200:
        msg = (
            f"Status {data.status_code} when getting solc versions from Github:"
            f" '{data.json()['message']}'"
        )
        if data.status_code == 403:
            msg += (
                "\n\nIf this issue persists, generate a Github API token and store"
                " it as the environment variable `GITHUB_TOKEN`:\n"
                "https://github.blog/2013-05-16-personal-api-tokens/"
            )
        raise ConnectionError(msg)

    for release in data.json():
        asset = next((i for i in release["assets"] if re.match(pattern, i["name"])), False)
        if asset:
            version = Version.coerce(release["tag_name"].lstrip("v"))
            version_list.append(version)
        if release["tag_name"] == MINIMAL_SOLC_VERSION:
            break
    return sorted(version_list, reverse=True)


def _select_pragma_version(pragma_string: str, version_list: List[Version]) -> Optional[Version]:
    comparator_set_range = pragma_string.replace(" ", "").split("||")
    comparator_regex = re.compile(r"(([<>]?=?|\^)\d+\.\d+\.\d+)+")
    version = None

    for comparator_set in comparator_set_range:
        spec = SimpleSpec(*(i[0] for i in comparator_regex.findall(comparator_set)))
        selected = spec.select(version_list)
        if selected and (not version or version < selected):
            version = selected

    return version


def get_installed_solc_versions(solcx_binary_path: Union[Path, str] = None) -> List[Version]:
    install_path = get_solc_folder(solcx_binary_path)
    return sorted([Version(i.name[6:]) for i in install_path.glob("solc-v*")], reverse=True)


def install_solc(
    version: Union[str, Version],
    allow_osx: bool = False,
    show_progress: bool = False,
    solcx_binary_path: Union[Path, str] = None,
) -> None:

    arch = _get_arch()
    platform = _get_platform()
    version = _convert_and_validate_version(version)

    lock = get_process_lock(version)
    lock.acquire(True)

    try:
        if _check_for_installed_version(version, solcx_binary_path):
            path = get_solc_folder(solcx_binary_path).joinpath(f"solc-v{version}")
            LOGGER.info(f"solc {version} already installed at: {path}")
            return

        if arch == "arm":
            _install_solc_arm(version, show_progress, solcx_binary_path)
        elif platform == "linux":
            _install_solc_linux(version, show_progress, solcx_binary_path)
        elif platform == "darwin":
            _install_solc_osx(version, allow_osx, show_progress, solcx_binary_path)
        elif platform == "win32":
            _install_solc_windows(version, show_progress, solcx_binary_path)
        binary_path = get_executable(version, solcx_binary_path)
        _check_subprocess_call(
            [str(binary_path), "--version"],
            message=f"Checking installed executable version at: {binary_path}",
        )
        if not solc_version:
            set_solc_version(version)
            LOGGER.info(f"solc {version} successfully installed at: {binary_path}")
    finally:
        lock.release()


def _check_subprocess_call(command, message=None, verbose=False, **proc_kwargs):
    if message:
        LOGGER.debug(message)
    LOGGER.info(f"Executing: {' '.join(command)}")

    return subprocess.check_call(
        command, stderr=subprocess.STDOUT if verbose else subprocess.DEVNULL, **proc_kwargs
    )


def _chmod_plus_x(executable_path):
    executable_path.chmod(executable_path.stat().st_mode | stat.S_IEXEC)


def _check_for_installed_version(
    version: Version, solcx_binary_path: Union[Path, str] = None
) -> bool:
    path = get_solc_folder(solcx_binary_path).joinpath(f"solc-v{version}")
    return path.exists()


def _get_temp_folder():
    path = Path(tempfile.gettempdir()).joinpath(f"solcx-tmp-{os.getpid()}")
    if path.exists():
        shutil.rmtree(str(path))
    path.mkdir()
    return path


def _download_solc(url, show_progress):
    response = requests.get(url, stream=show_progress)
    if response.status_code == 404:
        raise DownloadError(
            "404 error when attempting to download from {} - are you sure this"
            " version of solidity is available?".format(url)
        )
    if response.status_code != 200:
        raise DownloadError(
            f"Received status code {response.status_url} when attempting to download from {url}"
        )
    if not show_progress:
        return response.content

    total_size = int(response.headers.get("content-length", 0))
    progress_bar = tqdm(total=total_size, unit="iB", unit_scale=True)
    content = bytes()

    for data in response.iter_content(1024, decode_unicode=True):
        progress_bar.update(len(data))
        content += data
    progress_bar.close()

    return content


def _install_solc_linux(
    version: Version, show_progress: bool, solcx_binary_path: Union[Path, str, None]
) -> None:
    download = DOWNLOAD_BASE.format(version, "solc-static-linux")
    install_path = get_solc_folder(solcx_binary_path).joinpath(f"solc-v{version}")

    LOGGER.info(f"Downloading solc {version} from {download}")
    content = _download_solc(download, show_progress)
    with open(install_path, "wb") as fp:
        fp.write(content)
    _chmod_plus_x(install_path)


def _install_solc_windows(
    version: Version, show_progress: bool, solcx_binary_path: Union[Path, str, None]
) -> None:
    download = DOWNLOAD_BASE.format(version, "solidity-windows.zip")
    install_path = get_solc_folder(solcx_binary_path).joinpath(f"solc-v{version}")

    temp_path = _get_temp_folder()
    content = _download_solc(download, show_progress)
    with zipfile.ZipFile(BytesIO(content)) as zf:
        zf.extractall(str(temp_path))

    temp_path.rename(install_path)


def _install_solc_arm(
    version: Version, show_progress: bool, solcx_binary_path: Union[Path, str, None]
) -> None:
    _compile_solc(version, show_progress, solcx_binary_path)


def _install_solc_osx(
    version: Version,
    allow_osx: bool,
    show_progress: bool,
    solcx_binary_path: Union[Path, str, None],
) -> None:
    if version < Version("0.5.0") and not allow_osx:
        raise ValueError(
            "Installing solc {0} on OSX often fails. For suggested installation options:\n"
            "https://github.com/iamdefinitelyahuman/py-solc-x/wiki/Installing-Solidity-on-OSX\n\n"
            "To ignore this warning and attempt to install: "
            "solcx.install_solc('{0}', allow_osx=True)".format(version)
        )
    else:
        _compile_solc(version, show_progress, solcx_binary_path)


def _compile_solc(
    version: Version, show_progress: bool, solcx_binary_path: Union[Path, str, None]
) -> None:
    temp_path = _get_temp_folder()
    download = DOWNLOAD_BASE.format(version, f"solidity_{version}.tar.gz")
    install_path = get_solc_folder(solcx_binary_path).joinpath(f"solc-v{version}")

    content = _download_solc(download, show_progress)
    with tarfile.open(fileobj=BytesIO(content)) as tar:
        tar.extractall(temp_path)
    temp_path = temp_path.joinpath(f"solidity_{version[1:]}")

    try:
        _check_subprocess_call(
            ["sh", str(temp_path.joinpath("scripts/install_deps.sh"))],
            message="Running dependency installation script `install_deps.sh`",
        )
    except subprocess.CalledProcessError as e:
        LOGGER.warning(e, exc_info=True)

    original_path = os.getcwd()
    temp_path.joinpath("build").mkdir(exist_ok=True)
    os.chdir(str(temp_path.joinpath("build").resolve()))
    try:
        for cmd in (["cmake", ".."], ["make"]):
            _check_subprocess_call(cmd, message=f"Running {cmd[0]}")
        temp_path.joinpath("build/solc/solc").rename(install_path)
    except subprocess.CalledProcessError as e:
        raise OSError(
            f"{cmd[0]} returned non-zero exit status {e.returncode}"
            " while attempting to build solc from the source.\n"
            "This is likely due to a missing or incorrect version of a build dependency.\n\n"
            "For suggested installation options: "
            "https://github.com/iamdefinitelyahuman/py-solc-x/wiki/Installing-Solidity-on-OSX"
        )
    finally:
        os.chdir(original_path)

    _chmod_plus_x(install_path)


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("version")
    argument_parser.add_argument("--solcx-binary-path", default=None)
    args = argument_parser.parse_args()
    install_solc(args.version, solcx_binary_path=args.solcx_binary_path)
