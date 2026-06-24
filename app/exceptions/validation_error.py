from .account_exception import AccountException

class ValidationError(AccountException):
    """Raised when validation fails."""
    
    def __init__(self, field: str, message: str):
        super().__init__(
            f"Validation error in {field}: {message}",
            "VALIDATION_ERROR"
        )
