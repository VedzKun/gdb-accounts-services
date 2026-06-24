from .account_exception import AccountException

class AccountAlreadyExistsError(AccountException):
    """Raised when account already exists."""
    
    def __init__(self, name: str, dob: str = None):
        msg = f"Account with name '{name}'"
        if dob:
            msg += f" and DOB '{dob}'"
        msg += " already exists"
        super().__init__(msg, "ACCOUNT_ALREADY_EXISTS")
