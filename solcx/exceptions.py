from typing import Optional

DEFAULT_MESSAGE = "An error occurred during execution"


class SolcError(Exception):
    message = DEFAULT_MESSAGE

    def __init__(
        self,
        command: list,
        return_code: Optional[int],
        stdin_data: Optional[str],
        stdout_data: Optional[str],
        stderr_data: Optional[str],
        message: Optional[str] = None,
    ) -> None:
        if message is not None:
            self.message = message
        self.command = command
        self.return_code = return_code
        self.stdin_data = stdin_data
        self.stderr_data = stderr_data
        self.stdout_data = stdout_data

    def __str__(self) -> str:
        return (
            f"{self.message}"
            f"\n> command: `{' '.join(self.command)}`"
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


class UnexpectedVersionError(Exception):
    pass


class SolcNotInstalled(Exception):
    pass


class DownloadError(Exception):
    pass


class UnexpectedVersionWarning(Warning):
    pass
