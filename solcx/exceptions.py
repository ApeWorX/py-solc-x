import textwrap

DEFAULT_MESSAGE = "An error occurred during execution"


class SolcError(Exception):
    message = DEFAULT_MESSAGE

    def __init__(self, command, return_code, stdin_data, stdout_data, stderr_data, message=None):
        if message is not None:
            self.message = message
        self.command = command
        self.return_code = return_code
        self.stdin_data = stdin_data
        self.stderr_data = stderr_data
        self.stdout_data = stdout_data

    def __str__(self):
        return textwrap.dedent(
            f"""
            {self.message}
            > command: `{' '.join(self.command)}`
            > return code: `{self.return_code}`
            > stdout:
            {self.stdout_data}
            > stderr:
            {self.stderr_data}
            """
        ).strip()


class ContractsNotFound(SolcError):
    message = "No contracts found during compilation"


class SolcNotInstalled(Exception):
    pass


class DownloadError(Exception):
    pass
