from .account_exception import AccountException

class DatabaseError(AccountException):
    """Raised when database operation fails."""
    
    def __init__(self, message: str):
        super().__init__(
            f"Database error: {message}",
            "DATABASE_ERROR"
        )
