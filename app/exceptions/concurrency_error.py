from .account_exception import AccountException

class ConcurrencyError(AccountException):
    """Raised when concurrent operation causes conflict."""
    
    def __init__(self, account_number: int):
        super().__init__(
            f"Concurrent operation on account {account_number}. Please retry",
            "CONCURRENCY_ERROR"
        )
