from .account_exception import AccountException

class AccountAlreadyActiveError(AccountException):
    """Raised when trying to activate an already active account."""
    
    def __init__(self, account_number: int):
        super().__init__(
            f"Account {account_number} is already active",
            "ACCOUNT_ALREADY_ACTIVE"
        )
