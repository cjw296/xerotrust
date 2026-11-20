from click import ClickException


class XeroAPIException(ValueError):
    """
    An error occurred when interacting with the Xero API
    """


class RateLimitDeferred(ClickException):
    """
    An incomplete export must be retried later instead of waiting in this process.
    """

    exit_code = 75
    endpoint: str | None = None

    def format_message(self) -> str:
        message = super().format_message()
        return f'{self.endpoint}: {message}' if self.endpoint else message
