
class AccountException(Exception):
    """Base exception for all account-related errors."""
    
    def __init__(self, message: str, error_code: str = "ACCOUNT_ERROR"):
        """
        Initialize account exception.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
