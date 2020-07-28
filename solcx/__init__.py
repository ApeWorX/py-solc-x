from solcx.install import (
    get_available_solc_versions,
    get_installed_solc_versions,
    get_solcx_install_folder,
    import_installed_solc,
    install_solc,
    install_solc_pragma,
    set_solc_version,
    set_solc_version_pragma,
)
from solcx.main import compile_files, compile_source, compile_standard, get_solc_version, link_code

# check for installed version of solc
import_installed_solc()

# default to latest version
if get_installed_solc_versions():
    set_solc_version(get_installed_solc_versions()[-1], silent=True)
