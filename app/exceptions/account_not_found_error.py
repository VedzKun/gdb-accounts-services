from .account_exception import AccountException

class AccountNotFoundError(AccountException):
    """Raised when account does not exist."""
    
    def __init__(self, account_number: int):
        super().__init__(
            f"Account {account_number} not found",
            "ACCOUNT_NOT_FOUND"
        )
