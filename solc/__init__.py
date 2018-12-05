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
)

if sys.version_info.major < 3:
    warnings.simplefilter('always', DeprecationWarning)
    warnings.warn(DeprecationWarning(
        "The `py-solc` library is dropping support for Python 2.  Upgrade to Python 3."
    ))
    warnings.resetwarnings()

solc_folder = __file__.rsplit('/', maxsplit=2)[0] + "/bin"

if not os.path.exists(solc_folder):
    os.mkdir(solc_folder)

if not get_installed_solc_versions():
    install_solc("v0.5.1")

set_solc_version(get_installed_solc_versions()[-1])