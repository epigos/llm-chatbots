class DoesNotExist(RuntimeError):
    """
    Exception raised when query returns no record.
    """


class AuthenticationError(RuntimeError):
    """
    Exception raised when user authentication fails.
    """
