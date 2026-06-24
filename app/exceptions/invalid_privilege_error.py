from .account_exception import AccountException

class InvalidPrivilegeError(AccountException):
    """Raised when privilege level is invalid."""
    
    def __init__(self, privilege: str):
        super().__init__(
            f"Invalid privilege: {privilege}. Must be PREMIUM, GOLD, or SILVER",
            "INVALID_PRIVILEGE"
        )
