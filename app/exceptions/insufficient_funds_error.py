from .account_exception import AccountException

class InsufficientFundsError(AccountException):
    """Raised when account balance is insufficient for transaction."""
    
    def __init__(self, balance: float, required: float):
        super().__init__(
            f"Insufficient funds. Balance: ₹{balance}, Required: ₹{required}",
            "INSUFFICIENT_FUNDS"
        )
