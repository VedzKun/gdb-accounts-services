from fastapi import Depends
from app.repositories.account_repo import AccountRepository
from app.services.account_service import AccountService
from app.services.internal_service import InternalAccountService

def get_account_repository() -> AccountRepository:
    """Provider for AccountRepository."""
    return AccountRepository()

def get_account_service() -> AccountService:
    """Provider for AccountService."""
    return AccountService()

def get_internal_service() -> InternalAccountService:
    """Provider for InternalAccountService."""
    return InternalAccountService()
