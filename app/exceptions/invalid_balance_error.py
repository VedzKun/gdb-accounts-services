from .account_exception import AccountException

class InvalidBalanceError(AccountException):
    """Raised when balance operation is invalid."""
    
    def __init__(self, message: str = "Invalid balance operation"):
        super().__init__(message, "INVALID_BALANCE")
