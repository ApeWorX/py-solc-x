from __future__ import absolute_import

import os
import sys
import warnings

from .main import (  # noqa: F401
    get_solc_version_string,
    get_solc_version,
    get_installed_solc_versions,
    set_solc_version,
    compile_files,
    compile_source,
    compile_standard,
    link_code,
)
from .install import (
    install_solc,
    get_solc_folder
)

solc_folder = get_solc_folder()
if not os.path.exists(solc_folder):
    os.mkdir(solc_folder)

if not get_installed_solc_versions():
    install_solc()

set_solc_version(get_installed_solc_versions()[-1])