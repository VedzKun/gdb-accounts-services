from .account_exception import AccountException

class AccountAlreadyInactiveError(AccountException):
    """Raised when trying to deactivate an already inactive account."""
    
    def __init__(self, account_number: int):
        super().__init__(
            f"Account {account_number} is already inactive",
            "ACCOUNT_ALREADY_INACTIVE"
        )
