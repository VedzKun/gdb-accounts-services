from .account_exception import AccountException

class OperationNotAllowedError(AccountException):
    """Raised when operation is not allowed on account."""
    
    def __init__(self, account_number: int, reason: str):
        super().__init__(
            f"Operation not allowed on account {account_number}: {reason}",
            "OPERATION_NOT_ALLOWED"
        )
