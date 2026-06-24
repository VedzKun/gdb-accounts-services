from .account_exception import AccountException

class AccountInactiveError(AccountException):
    """Raised when trying to operate on inactive account."""
    
    def __init__(self, account_number: int):
        super().__init__(
            f"Account {account_number} is inactive",
            "ACCOUNT_INACTIVE"
        )
