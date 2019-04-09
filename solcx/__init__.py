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
    import_installed_solc,
    install_solc,
    get_installed_solc_versions,
    get_solc_folder,
    set_solc_version
)

# check for installed version of solc
import_installed_solc()

# if no installed version, download
if not get_installed_solc_versions():
    print("Cannot find solc, installing...")
    install_solc()

# default to latest version
set_solc_version(get_installed_solc_versions()[-1])