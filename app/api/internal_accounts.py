"""
Accounts Service - Internal API Routes

Service-to-service REST API endpoints.
Called only by other microservices (Transactions, Auth).
NOT publicly exposed.

Author: GDB Architecture Team
"""

import logging
from fastapi import APIRouter, HTTPException, status, Depends

from app.services.internal_service import InternalAccountService
from app.exceptions.account_exceptions import AccountException

from app.dependencies.providers import get_internal_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ========================================
# INTERNAL ACCOUNT INFORMATION
# ========================================

@router.get(
    "/accounts/{account_number}",
    tags=["Internal - Account Info"],
    summary="Get Account Details (Internal)",
    description="Fetch account details for inter-service use. Internal API only."
)
async def get_account_details_internal(
    account_number: int,
    internal_service: InternalAccountService = Depends(get_internal_service)
):
    """
    Get account details for service-to-service use.
    """
    try:
        details = await internal_service.get_account_details(account_number)
        return details
        
    except AccountException as e:
        logger.error(f"❌ Get account details failed: {e.error_code}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "NOT_FOUND" in e.error_code else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": str(e)}
        )


@router.get(
    "/accounts/{account_number}/privilege",
    tags=["Internal - Account Info"],
    summary="Get Account Privilege (Internal)",
)
async def get_privilege_internal(
    account_number: int,
    internal_service: InternalAccountService = Depends(get_internal_service)
):
    """
    Get account privilege level.
    """
    try:
        result = await internal_service.get_privilege(account_number)
        return result
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": str(e)}
        )


@router.get(
    "/accounts/{account_number}/active",
    tags=["Internal - Account Info"],
    summary="Check Account Active Status (Internal)",
)
async def check_account_active_internal(
    account_number: int,
    internal_service: InternalAccountService = Depends(get_internal_service)
):
    """
    Check if account is active.
    """
    try:
        result = await internal_service.check_account_active(account_number)
        return result
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": str(e)}
        )


# ========================================
# INTERNAL DEBIT/CREDIT OPERATIONS
# ========================================

@router.post(
    "/accounts/{account_number}/debit",
    tags=["Internal - Transactions"],
    summary="Debit Account (Internal)",
)
async def debit_account_internal(
    account_number: int,
    amount: float,
    description: str = "Internal Debit",
    internal_service: InternalAccountService = Depends(get_internal_service),
):
    """
    Debit amount from account.
    """
    try:
        result = await internal_service.debit_for_transfer(
            account_number,
            amount
        )
        status_code = status.HTTP_200_OK if result["status"] == "SUCCESS" else status.HTTP_400_BAD_REQUEST
        return result
    except Exception as e:
        logger.error(f"❌ Debit failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": str(e)}
        )


@router.post(
    "/accounts/{account_number}/credit",
    tags=["Internal - Transactions"],
    summary="Credit Account (Internal)",
)
async def credit_account_internal(
    account_number: int,
    amount: float,
    description: str = "Internal Credit",
    internal_service: InternalAccountService = Depends(get_internal_service),
):
    """
    Credit amount to account.
    """
    try:
        result = await internal_service.credit_for_transfer(
            account_number,
            amount
        )
        status_code = status.HTTP_200_OK if result["status"] == "SUCCESS" else status.HTTP_400_BAD_REQUEST
        return result
    except Exception as e:
        logger.error(f"❌ Credit failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": str(e)}
        )


# ========================================
# INTERNAL SECURITY OPERATIONS
# ========================================

@router.post(
    "/accounts/{account_number}/verify-pin",
    tags=["Internal - Security"],
    summary="Verify Account PIN (Internal)",
)
async def verify_pin_internal(
    account_number: int,
    pin: str,
    internal_service: InternalAccountService = Depends(get_internal_service),
):
    """
    Verify account PIN.
    """
    try:
        result = await internal_service.verify_account_pin(account_number, pin)
        if not result.get("pin_valid", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error_code": result.get("error_code", "INVALID_PIN"), "message": "PIN verification failed"}
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ PIN verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": str(e)}
        )
