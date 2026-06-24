from .account_exception import AccountException

class InvalidAadharNumberError(AccountException):
    """Raised when Aadhar number validation fails."""
    
    def __init__(self, aadhar_number: str, message: str = "Invalid Aadhar number"):
        super().__init__(
            f"{message}: {aadhar_number}",
            "INVALID_AADHAR_NUMBER"
        )
