from .account_exception import AccountException

class InvalidAccountTypeError(AccountException):
    """Raised when account type is invalid."""
    
    def __init__(self, account_type: str):
        super().__init__(
            f"Invalid account type: {account_type}. Must be SAVINGS or CURRENT",
            "INVALID_ACCOUNT_TYPE"
        )
