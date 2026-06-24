from .account_exception import AccountException

class DuplicateConstraintError(AccountException):
    """Raised when unique constraint is violated."""
    
    def __init__(self, constraint: str):
        super().__init__(
            f"Duplicate value violates constraint: {constraint}",
            "DUPLICATE_CONSTRAINT"
        )
