from .account_exception import AccountException

class InvalidPinError(AccountException):
    """Raised when PIN is invalid."""
    
    def __init__(self, message: str = "PIN verification failed"):
        super().__init__(message, "INVALID_PIN")
