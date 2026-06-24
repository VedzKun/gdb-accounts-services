from .account_exception import AccountException

class AccountClosedError(AccountException):
    """Raised when trying to operate on closed account."""
    
    def __init__(self, account_number: int):
        super().__init__(
            f"Account {account_number} is closed",
            "ACCOUNT_CLOSED"
        )
