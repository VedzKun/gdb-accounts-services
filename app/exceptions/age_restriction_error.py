from .account_exception import AccountException

class AgeRestrictionError(AccountException):
    """Raised when account holder is underage."""
    
    def __init__(self, age: int):
        super().__init__(
            f"Account holder must be at least 18 years old (Current age: {age})",
            "AGE_RESTRICTION"
        )
