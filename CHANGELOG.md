# CHANGELOG

**NOTE**: This Changelog is no longer used, since ApeWorX acquired ths project.
The changelog can now be found in the GitHub's release notes.
Everything below this line is part of the original Changelog:

______________________________________________________________________

All notable changes to this project are documented in this file.

This changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This project was forked from `py-solc`. View the original changelog [here](https://github.com/ethereum/py-solc/blob/master/CHANGELOG).

## [Unreleased](https://github.com/iamdefinitelyahuman/py-solc-x)

## [1.1.1](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v1.1.1) - 2021-10-12

### Fixed

- Invalid default compiler outputs ([#127](https://github.com/iamdefinitelyahuman/py-solc-x/pull/127))

## [1.1.0](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v1.1.0) - 2020-12-28

### Added

- Optional kwarg `with_commit_hash` in `solcx.get_solc_version` ([#120](https://github.com/iamdefinitelyahuman/py-solc-x/pull/120))

### Fixed

- Handle ABI format for Solidity 0.8.0 ([#119](https://github.com/iamdefinitelyahuman/py-solc-x/pull/119))

## [1.0.2](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v1.0.2) - 2020-12-10

### Fixed

- Convert `Path` to `str` prior to calling `subprocess` ([#117](https://github.com/iamdefinitelyahuman/py-solc-x/pull/117))

## [1.0.1](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v1.0.1) - 2020-11-20

### Fixed

- Improve `solc` version detection and raise correct error if it fails ([#110](https://github.com/iamdefinitelyahuman/py-solc-x/pull/110))
- Correctly handle standalone Windows executables ([#112](https://github.com/iamdefinitelyahuman/py-solc-x/pull/112))
- Correctly handle non-standard tagged versions from Github API ([#113](https://github.com/iamdefinitelyahuman/py-solc-x/pull/113))

## [1.0.0](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v1.0.0) - 2020-08-26

### Added

- "latest" is a valid version number when installing ([#104](https://github.com/iamdefinitelyahuman/py-solc-x/pull/104))
- Custom exception classes ([#103](https://github.com/iamdefinitelyahuman/py-solc-x/pull/103))
- Main compiler functions have `solc_version` and `solc_binary` kwargs for setting the version or using a custom solc binary ([#98](https://github.com/iamdefinitelyahuman/py-solc-x/pull/98))
- MyPy types ([#99](https://github.com/iamdefinitelyahuman/py-solc-x/pull/99))

### Changed

- Major refactor of the main compiler functions and low-level solc wrapper ([#96](https://github.com/iamdefinitelyahuman/py-solc-x/pull/96))
- Binaries are installed from [solc-bin.ethereum.org](https://solc-bin.ethereum.org/) instead of Github ([#108](https://github.com/iamdefinitelyahuman/py-solc-x/pull/108))
- Building from source is now handled by a separate function `solcx.install.compile_solc` ([#108](https://github.com/iamdefinitelyahuman/py-solc-x/pull/108))
- `get_available_solc_versions` has been split into `get_installable_solc_versions` and `get_compilable_solc_versions` ([#108](https://github.com/iamdefinitelyahuman/py-solc-x/pull/108))
- `get_solc_folder` is now `get_solcx_install_folder` ([#102](https://github.com/iamdefinitelyahuman/py-solc-x/pull/102))
- Paths are represented as `Path` objects instead of strings ([#97](https://github.com/iamdefinitelyahuman/py-solc-x/pull/97))
- Solc versions are represented as `semantic_version.Version` objects instead of strings ([#93](https://github.com/iamdefinitelyahuman/py-solc-x/pull/93))

### Removed

- `utils.string` and `utils.types` subpackages ([#95](https://github.com/iamdefinitelyahuman/py-solc-x/pull/95))

## [0.10.1](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.10.1) - 2020-07-17

### Fixed

- Support ARM 64 bit architecture (`aarch64`)
- always include `-` for calls using stdin

## [0.10.0](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.10.0) - 2020-06-18

### Added

- Check architecture prior to installation, compile when `arm`

## [0.9.0](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.9.0) - 2020-06-10

### Added

- Add `base_path` as a possible wrapper kwarg

### Fixed

- handle `stderr` output when calling `which`
- expect return code 1 when using `--help`

## [0.8.2](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.8.2) - 2020-05-11

### Changed

- Improve error message on failed OSX installation

### Fixed

- `TypeError` when download fails using progress bar

## [0.8.1](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.8.1) - 2020-03-26

### Fixed

- Bugfix: setting version with pragma
- Expand error message on 403 error from Github ABI

## [0.8.0](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.8.0) - 2020-02-19

### Added

- Allow user-specified installation directory via `SOLCX_BINARY_PATH` environment variable
- Include `which` when importing installed versions on OSX

## [0.7.2](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.7.2) - 2020-02-05

### Fixed

- include PID in install temp path to avoid process collisions

## [0.7.1](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.7.1) - 2020-02-05

### Fixed

- compiling with limited output values

## [0.7.0](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.7.0) - 2019-12-32

### Added

- Add locks for thread and multiprocessing safety
- Show progress bar during installation if `tqdm` is installed

### Changed

- Store solc binaries at $HOME/.solcx

## [0.6.1](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.6.1) - 2019-12-19

### Fixed

- Fix compatibility issues with Solidity 0.6.0
- When installing on OSX, log a warning instead of raising if dependency installation fails
- Ensure old versions are still visible in solcx.get_available_solc_versions

## [0.6.0](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.6.0) - 2019-09-06

### Changed

- Use logger instead of print statements
- Use requests package for downloads on all platforms

### Fixed

- Update dependencies, fix deprecation warnings

## [0.5.0](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.5.0) - 2019-07-30

### Added

- Support for github API tokens via environment var GITHUB_TOKEN
- Improved verbosity when get_available_solc_versions raises

### Removed

- Remove interace flag (was removed from solc in 0.4.0)
- Raise on clone-bin and formal flags when using 0.5.x

## [0.4.2](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.4.2) - 2019-07-27

### Fixed

- Fix link_code to support 0.5.x
- Remove trailing whitespace on solcx.get_version_string - fixes windows 0.5.x bug

## [0.4.1](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.4.1) - 2019-07-14

### Added

- Allow silencing of console output when changing solc version

### Fixed

- absolute paths on windows systems

## [0.4.0](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.4.0) - 2019-05-07

### Changed

- set_solc_version raises instead of installing when requested version is not installed
- Do not allow version=None on installer methods

### Fixed

- Install new versions into solcx/temp - prevents issues with aborted installs

## [0.3.0](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.3.0) - 2019-05-01

### Added

- Install and set solc version based on pragma
- Get available solc versions, only install version if available for user's OS

## [0.2.1](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.2.1) - 2019-04-14

### Fixed

- Bugfix when no installed version of solc is found
- Confirm that imported versions of solc are still working

## [0.2.0](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.2.0) - 2019-04-09

### Added

- Linux - copy from `which solc` path to save time installing solc
- OSX - copy solc versions from `usr/local/Cellar`, raise when attempting v0.4.x install

### Changed

- `install.py` - replace `os.path` with `pathlib.Path`

### Fixed

- Fix "No input files given" bug in `solcx.compile_source()` on v0.5.x

## [0.1.1](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.1.1) - 2019-0213

### Fixed

- Better verbosity when building from source fails

## [0.1.0](https://github.com/iamdefinitelyahuman/py-solc-x/releases/tag/v0.1.0) - 2019-01-26

### Added

- Support for `solc 0.5.x`
- Add Windows installer
- Change active solc version with `solcx.set_solc_version`

### Changed

- Change install location to ./solcx/bin - no longer uses standard installed verion

### Removed

- Drop support for `solc < 0.4.11`
