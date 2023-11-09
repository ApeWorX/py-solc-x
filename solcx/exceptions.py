from typing import Dict, List, Optional


class SolcError(Exception):
    message = "An error occurred during execution"

    def __init__(
        self,
        message: Optional[str] = None,
        command: Optional[List[str]] = None,
        return_code: Optional[int] = None,
        stdin_data: Optional[str] = None,
        stdout_data: Optional[str] = None,
        stderr_data: Optional[str] = None,
        error_dict: Optional[Dict] = None,
    ) -> None:
        if message is not None:
            self.message = message
        self.command = command or []
        self.return_code = return_code
        self.stdin_data = stdin_data
        self.stderr_data = stderr_data
        self.stdout_data = stdout_data
        self.error_dict = error_dict

    def __str__(self) -> str:
        return (
            f"{self.message}"
            f"\n> command: `{' '.join(str(i) for i in self.command)}`"
            f"\n> return code: `{self.return_code}`"
            "\n> stdout:"
            f"\n{self.stdout_data}"
            "\n> stderr:"
            f"\n{self.stderr_data}"
        ).strip()


class ContractsNotFound(SolcError):
    message = "No contracts found during compilation"


class SolcInstallationError(Exception):
    pass


class UnknownOption(AttributeError):
    pass


class UnknownValue(ValueError):
    pass


class UnexpectedVersionError(Exception):
    pass


class UnsupportedVersionError(ValueError):
    pass


class SolcNotInstalled(Exception):
    pass


class DownloadError(Exception):
    pass


class UnexpectedVersionWarning(Warning):
    pass
