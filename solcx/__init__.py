from __future__ import absolute_import

import os

from .main import (  # noqa: F401
    get_solc_version_string,
    get_solc_version,
    compile_files,
    compile_source,
    compile_standard,
    link_code,
)
from .install import (
    install_solc,
    get_installed_solc_versions,
    get_solc_folder,
    set_solc_version
)

# check for an installed version of solc
# install if none found
# default to latest version

if not os.path.exists(get_solc_folder()):
    os.mkdir(get_solc_folder())

if not get_installed_solc_versions():
    print("Cannot find solc, installing...")
    install_solc()

set_solc_version(get_installed_solc_versions()[-1])