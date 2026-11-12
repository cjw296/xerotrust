class XeroAPIException(ValueError):
    """
    An error occurred when interacting with the Xero API
    """


class RateLimitDeferred(RuntimeError):
    """An incomplete export must be retried later instead of waiting in this process."""
