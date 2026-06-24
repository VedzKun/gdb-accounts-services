from .account_exception import AccountException

class InvalidRegistrationNumberError(AccountException):
    """Raised when company registration validation fails."""
    
    def __init__(self, registration_no: str, message: str = "Invalid company registration number"):
        super().__init__(
            f"{message}: {registration_no}",
            "INVALID_REGISTRATION_NUMBER"
        )
