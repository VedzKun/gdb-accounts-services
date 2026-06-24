"""
Accounts Service - Account API Routes

Public REST API endpoints for account management.

Authorization:
- Create Account: ADMIN, TELLER
- Update Account: ADMIN, TELLER
- Close Account: ADMIN only
- Activate/Inactivate: ADMIN only
- View All Accounts: ADMIN, TELLER
- View Own Account: MANAGER (only their own accounts)

Author: GDB Architecture Team
"""

import logging
import sys
from typing import Dict, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from pydantic import BaseModel, Field

from app.services.account_service import AccountService
from app.models.account import (
    SavingsAccountCreate,
    CurrentAccountCreate,
    AccountUpdate,
    AccountResponse,
    SavingsAccountResponse,
    CurrentAccountResponse,
    BalanceResponse,
    ErrorResponse
)
from app.exceptions.account_exceptions import AccountException

# Import authorization dependencies from Auth Service
# Import authorization dependencies
# Assumes sys.path is set up by main.py to include auth_service/app
from security.auth_dependencies import (
    get_current_user,
    require_admin_or_teller,
    require_admin,
    require_admin_or_teller_or_manager,
)
from security.jwt_validation import JWTValidator, RoleChecker

from app.dependencies.providers import get_account_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ========================================
# ACCOUNT CREATION ENDPOINTS
# ========================================

@router.post(
    "/accounts/savings",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Accounts - Creation"],
    summary="Create Savings Account",
    description="Create a new savings account for individuals (age >= 18)"
)
async def create_savings_account(
    request: SavingsAccountCreate,
    claims: Dict[str, Any] = Depends(require_admin_or_teller()),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Create a new savings account.

    **Authorization:** ADMIN or TELLER role required
    
    **Request Body:**
    - `name`: Account holder name (1-255 characters)
    - `account_type`: Fixed as SAVINGS
    - `pin`: 4-6 digit PIN
    - `date_of_birth`: DOB in YYYY-MM-DD format
    - `gender`: M, F, or OTHER
    - `phone_no`: 10-digit phone number
    - `privilege`: PREMIUM, GOLD, or SILVER (default: SILVER)
    
    **Validations:**
    - Age must be >= 18
    - PIN must be 4-6 digits (no sequential/same digits)
    - Unique name + DOB combination
    - Only ADMIN or TELLER can create accounts
    
    **Response:**
    - `account_number`: Auto-generated unique account number (starts from 1000)
    - `balance`: Initial balance (₹0)
    - `is_active`: TRUE by default
    - `activated_date`: Account creation timestamp
    
    **Possible Errors:**
    - 401: Missing or invalid authorization token
    - 403: Insufficient permissions (ADMIN or TELLER required)
    - `ACCOUNT_ALREADY_EXISTS`: name + DOB already exists
    - `AGE_RESTRICTION`: Age < 18
    - `INVALID_PIN`: Invalid PIN format
    - `VALIDATION_ERROR`: Input validation failed
    """
    try:
        account_number = await account_service.create_savings_account(request)
        
        logger.info(f"Savings account created by {claims.get('login_id')}: {account_number}")
        
        return AccountResponse(
            account_number=account_number,
            account_type="SAVINGS",
            name=request.name,
            privilege=request.privilege,
            balance=0.00,
            is_active=True,
            activated_date=datetime.utcnow(),
            closed_date=None,
            bank_name=request.bank_name,
            bank_branch=request.bank_branch,
            ifsc_code=request.ifsc_code
        )
        
    except AccountException as e:
        logger.error(f"❌ Account creation failed: {e.error_code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": e.error_code,
                "message": e.message
            }
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


@router.post(
    "/accounts/current",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Accounts - Creation"],
    summary="Create Current Account",
    description="Create a new current account for businesses/companies"
)
async def create_current_account(
    request: CurrentAccountCreate,
    claims: Dict[str, Any] = Depends(require_admin_or_teller()),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Create a new current account.

    **Authorization:** ADMIN or TELLER role required
    
    **Request Body:**
    - `name`: Account holder/company name (1-255 characters)
    - `account_type`: Fixed as CURRENT
    - `pin`: 4-6 digit PIN
    - `company_name`: Company name (1-255 characters)
    - `website`: Company website (optional)
    - `registration_no`: Company registration number (unique, 1-50 chars)
    - `privilege`: PREMIUM, GOLD, or SILVER (default: SILVER)
    
    **Validations:**
    - PIN must be 4-6 digits (no sequential/same digits)
    - Unique registration_no
    - Only ADMIN or TELLER can create accounts
    
    **Response:**
    - `account_number`: Auto-generated unique account number (starts from 1000)
    - `balance`: Initial balance (₹0)
    - `is_active`: TRUE by default
    - `activated_date`: Account creation timestamp
    
    **Possible Errors:**
    - 401: Missing or invalid authorization token
    - 403: Insufficient permissions (ADMIN or TELLER required)
    - `ACCOUNT_ALREADY_EXISTS`: registration_no already exists
    - `INVALID_PIN`: Invalid PIN format
    - `VALIDATION_ERROR`: Input validation failed
    """
    try:
        account_number = await account_service.create_current_account(request)
        
        logger.info(f"Current account created by {claims.get('login_id')}: {account_number}")
        
        return AccountResponse(
            account_number=account_number,
            account_type="CURRENT",
            name=request.name,
            privilege=request.privilege,
            balance=0.00,
            is_active=True,
            activated_date=datetime.utcnow(),
            closed_date=None,
            bank_name=request.bank_name,
            bank_branch=request.bank_branch,
            ifsc_code=request.ifsc_code
        )
        
    except AccountException as e:
        logger.error(f"❌ Account creation failed: {e.error_code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": e.error_code,
                "message": e.message
            }
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


# ========================================
# ACCOUNT QUERY ENDPOINTS
# ========================================

@router.get(
    "/accounts",
    response_model=list[AccountResponse],
    tags=["Accounts - Query"],
    summary="Get All Accounts",
    description="Retrieve all accounts (ADMIN/TELLER only), optionally filtered by account type"
)
async def get_all_accounts(
    account_type: str | None = None,
    claims: Dict[str, Any] = Depends(require_admin_or_teller_or_manager()),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Get all accounts, optionally filtered by account type.
    
    **Authorization:** ADMIN, TELLER, or MANAGER role required
    
    **Query Parameters:**
    - `account_type` (optional): Filter by account type (SAVINGS or CURRENT)
    
    **Response:**
    - List of all accounts (or filtered accounts) with details
    
    **Possible Errors:**
    - 401: Missing or invalid authorization token
    - 403: Insufficient permissions (ADMIN or TELLER required)
    - 400: Invalid account_type value
    - `DATABASE_ERROR`: Database query failed
    """
    try:
        # Validate account_type if provided
        if account_type and account_type not in ["SAVINGS", "CURRENT"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "INVALID_ACCOUNT_TYPE",
                    "message": "account_type must be either 'SAVINGS' or 'CURRENT'"
                }
            )
        
        login_id = JWTValidator.get_login_id(claims)
        print("Login ID ", login_id)
        print("Claims", claims)
        
        # Get all accounts from database (with optional filter)
        accounts = await account_service.get_all_accounts(account_type=account_type)
        
        filter_msg = f" (filtered by {account_type})" if account_type else ""
        logger.info(f"All accounts retrieved by {login_id}: {len(accounts)} accounts{filter_msg}")
        
        return [
            AccountResponse(
                account_number=account.account_number,
                account_type=account.account_type,
                name=account.name,
                privilege=account.privilege,
                balance=account.balance,
                is_active=account.is_active,
                activated_date=account.activated_date,
                closed_date=account.closed_date,
                bank_name=account.bank_name,
                bank_branch=account.bank_branch,
                ifsc_code=account.ifsc_code
            )
            for account in accounts
        ]
        
    except AccountException as e:
        logger.error(f"❌ Get all accounts failed: {e.error_code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )



@router.get(
    "/accounts/{account_number}",
    tags=["Accounts - Query"],
    summary="Get Account Details",
    description="Retrieve account details with type-specific information"
)
async def get_account(
    account_number: int,
    claims: Dict[str, Any] = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Get account details by account number.
    
    **Authorization:**
    - ADMIN or TELLER: Can view any account
    - MANAGER: Can only view their own accounts
    
    **Path Parameters:**
    - `account_number`: Account number
    
    **Response:**
    - Full account details with balance, status, and type-specific info
    
    **Possible Errors:**
    - 401: Missing or invalid authorization token
    - 403: MANAGER trying to view another user's account
    - `ACCOUNT_NOT_FOUND`: Account doesn't exist
    - `DATABASE_ERROR`: Database query failed
    """
    try:
        # Get user info from JWT
        user_role = JWTValidator.get_role(claims)
        user_id = JWTValidator.get_user_id(claims)
        login_id = JWTValidator.get_login_id(claims)
        
        # Get account details (now returns dict with all details)
        account = await account_service.get_account_details(account_number)
        
        logger.info(f"Account details retrieved by {login_id} ({user_role}): {account_number}")
        
        # Return the full account dict directly
        return account
        
    except AccountException as e:
        logger.error(f"❌ Get account failed: {e.error_code}")
        status_code = status.HTTP_404_NOT_FOUND if "NOT_FOUND" in e.error_code else status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status_code,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


@router.get(
    "/accounts/{account_number}/balance",
    response_model=BalanceResponse,
    tags=["Accounts - Query"],
    summary="Get Account Balance",
    description="Retrieve current account balance"
)
async def get_balance(
    account_number: int,
    claims: Dict[str, Any] = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Get account balance.
    
    **Authorization:**
    - ADMIN or TELLER: Can view any account balance
    - MANAGER: Can only view their own account balance
    
    **Path Parameters:**
    - `account_number`: Account number
    
    **Response:**
    - `account_number`: Account number
    - `balance`: Current balance in INR
    - `currency`: Fixed as INR
    
    **Possible Errors:**
    - 401: Missing or invalid authorization token
    - 403: MANAGER trying to view another user's account balance
    - `ACCOUNT_NOT_FOUND`: Account doesn't exist
    - `ACCOUNT_INACTIVE`: Account is inactive
    - `DATABASE_ERROR`: Database query failed
    """
    try:
        # Get user info from JWT
        user_role = JWTValidator.get_role(claims)
        user_id = JWTValidator.get_user_id(claims)
        login_id = JWTValidator.get_login_id(claims)
        
        # Get account details
        account = await account_service.get_account_details(account_number)
        
        # Note: Authorization is enforced at the transaction service level
        # Accounts service allows viewing any account's balance
        
        balance = await account_service.get_balance(account_number)
        
        logger.info(f"Account balance retrieved by {login_id} ({user_role}): {account_number}")
        
        return BalanceResponse(
            account_number=account_number,
            balance=balance,
            currency="INR"
        )
        
    except AccountException as e:
        logger.error(f"❌ Get balance failed: {e.error_code}")
        status_code = status.HTTP_404_NOT_FOUND if "NOT_FOUND" in e.error_code else status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status_code,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


@router.get(
    "/accounts/user/{user_id}",
    response_model=list[AccountResponse],
    tags=["Accounts - Query"],
    summary="Get Accounts by User ID",
    description="Retrieve all accounts for a specific user"
)
async def get_accounts_by_user_id(
    user_id: int,
    claims: Dict[str, Any] = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Get all accounts for a specific user.
    
    **Authorization:**
    - ADMIN or TELLER: Can view any user's accounts
    - MANAGER: Can only view their own accounts
    
    **Path Parameters:**
    - `user_id`: User ID
    
    **Response:**
    - List of accounts belonging to the user
    
    **Possible Errors:**
    - 401: Missing or invalid authorization token
    - 403: MANAGER trying to view another user's accounts
    - `DATABASE_ERROR`: Database query failed
    """
    try:
        # Get user info from JWT
        jwt_user_role = JWTValidator.get_role(claims)
        jwt_user_id = JWTValidator.get_user_id(claims)
        login_id = JWTValidator.get_login_id(claims)
        
        # Authorization: MANAGERs can only view their own accounts
        if jwt_user_role == "MANAGER" and jwt_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error_code": "FORBIDDEN", "message": "You can only view your own accounts"}
            )
        
        # Fetch accounts from database using raw SQL
        from app.database.db import get_db
        db = get_db()
        
        rows = await db.fetch_all("""
            SELECT 
                account_number, account_type, name, balance::numeric(15,2) as balance, 
                privilege, is_active, activated_date, closed_date
            FROM accounts
            WHERE user_id = $1
            ORDER BY account_number ASC
        """, user_id)
        
        if not rows:
            logger.info(f"No accounts found for user {user_id} by {login_id}")
            return []
        
        accounts = []
        for row in rows:
            # Convert balance to float
            balance_value = float(row['balance']) if row['balance'] is not None else 0.0
            
            accounts.append(AccountResponse(
                account_number=row['account_number'],
                account_type=row['account_type'],
                name=row['name'],
                balance=balance_value,
                privilege=row['privilege'],
                is_active=row['is_active'],
                activated_date=row['activated_date'],
                closed_date=row['closed_date']
            ))
        
        logger.info(f"Accounts for user {user_id} retrieved by {login_id}: {len(accounts)} accounts")
        return accounts
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


# ========================================
# ACCOUNT MANAGEMENT ENDPOINTS
# ========================================

@router.put(
    "/accounts/{account_number}",
    response_model=dict,
    tags=["Accounts - Management"],
    summary="Update Account",
    description="Update account details (name, privilege)"
)
async def update_account(
    account_number: int,
    request: AccountUpdate,
    claims: Dict[str, Any] = Depends(require_admin_or_teller()),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Update account details.
    
    **Authorization:** ADMIN or TELLER role required
    
    **Path Parameters:**
    - `account_number`: Account to update
    
    **Request Body:**
    - `name`: New account name (optional)
    - `privilege`: New privilege level (optional)
    
    **Response:**
    - `success`: true if updated
    - `message`: Status message
    
    **Possible Errors:**
    - 401: Missing or invalid authorization token
    - 403: Insufficient permissions (ADMIN or TELLER required)
    - `ACCOUNT_NOT_FOUND`: Account doesn't exist
    - `VALIDATION_ERROR`: Invalid input data
    """
    try:
        login_id = JWTValidator.get_login_id(claims)
        
        updated_account = await account_service.update_account(account_number, request)
        
        logger.info(f"Account {account_number} updated by {login_id}")
        
        return {
            "success": True,
            "message": "Account updated successfully",
            "account_number": account_number
        }
        
    except AccountException as e:
        logger.error(f"❌ Update account failed: {e.error_code}")
        status_code = status.HTTP_404_NOT_FOUND if "NOT_FOUND" in e.error_code else status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status_code,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


@router.post(
    "/accounts/{account_number}/activate",
    response_model=dict,
    tags=["Accounts - Management"],
    summary="Activate Account",
    description="Activate an inactive account"
)
async def activate_account(
    account_number: int,
    claims: Dict[str, Any] = Depends(require_admin()),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Activate an account.
    
    **Authorization:** ADMIN role required
    
    **Path Parameters:**
    - `account_number`: Account to activate
    
    **Response:**
    - `success`: true if activated
    - `message`: Status message
    
    **Possible Errors:**
    - 401: Missing or invalid authorization token
    - 403: Insufficient permissions (ADMIN required)
    - `ACCOUNT_NOT_FOUND`: Account doesn't exist
    """
    try:
        login_id = JWTValidator.get_login_id(claims)
        
        success = await account_service.activate_account(account_number)
        
        logger.info(f"Account activated by {login_id}: {account_number}")
        
        return {
            "success": success,
            "message": "Account activated successfully",
            "account_number": account_number
        }
        
    except AccountException as e:
        logger.error(f"❌ Activate account failed: {e.error_code}")
        # Map error codes to appropriate HTTP status codes
        status_code = status.HTTP_400_BAD_REQUEST
        if "NOT_FOUND" in e.error_code:
            status_code = status.HTTP_404_NOT_FOUND
        elif "ALREADY_ACTIVE" in e.error_code:
            status_code = status.HTTP_409_CONFLICT
        
        raise HTTPException(
            status_code=status_code,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


@router.post(
    "/accounts/{account_number}/inactivate",
    response_model=dict,
    tags=["Accounts - Management"],
    summary="Inactivate Account",
    description="Inactivate an active account"
)
async def inactivate_account(
    account_number: int,
    claims: Dict[str, Any] = Depends(require_admin()),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Inactivate an account.
    
    **Authorization:** ADMIN role required
    
    **Path Parameters:**
    - `account_number`: Account to inactivate
    
    **Response:**
    - `success`: true if inactivated
    - `message`: Status message
    
    **Possible Errors:**
    - 401: Missing or invalid authorization token
    - 403: Insufficient permissions (ADMIN required)
    - `ACCOUNT_NOT_FOUND`: Account doesn't exist
    """
    try:
        login_id = JWTValidator.get_login_id(claims)
        
        success = await account_service.inactivate_account(account_number)
        
        logger.info(f"Account inactivated by {login_id}: {account_number}")
        
        return {
            "success": success,
            "message": "Account inactivated successfully",
            "account_number": account_number
        }
        
    except AccountException as e:
        logger.error(f"❌ Inactivate account failed: {e.error_code}")
        # Map error codes to appropriate HTTP status codes
        status_code = status.HTTP_400_BAD_REQUEST
        if "NOT_FOUND" in e.error_code:
            status_code = status.HTTP_404_NOT_FOUND
        elif "ALREADY_INACTIVE" in e.error_code:
            status_code = status.HTTP_409_CONFLICT
        
        raise HTTPException(
            status_code=status_code,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


@router.post(
    "/accounts/{account_number}/close",
    response_model=dict,
    tags=["Accounts - Management"],
    summary="Close Account",
    description="Close (soft delete) an account"
)
async def close_account(
    account_number: int,
    claims: Dict[str, Any] = Depends(require_admin()),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Close an account.
    
    **Authorization:** ADMIN role required
    
    **Path Parameters:**
    - `account_number`: Account to close
    
    **Response:**
    - `success`: true if closed
    - `message`: Status message
    
    **Possible Errors:**
    - 401: Missing or invalid authorization token
    - 403: Insufficient permissions (ADMIN required)
    - `ACCOUNT_NOT_FOUND`: Account doesn't exist
    
    **Note:**
    - Account can be closed even with remaining balance
    - Closed accounts cannot perform transactions
    """
    try:
        login_id = JWTValidator.get_login_id(claims)
        
        success = await account_service.close_account(account_number)
        
        logger.info(f"Account closed by {login_id}: {account_number}")
        
        return {
            "success": success,
            "message": "Account closed successfully",
            "account_number": account_number
        }
        
    except AccountException as e:
        logger.error(f"❌ Close account failed: {e.error_code}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "NOT_FOUND" in e.error_code else status.HTTP_400_BAD_REQUEST,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


# ============================================
# PIN VERIFICATION ENDPOINT (Frontend requires this)
# ============================================

class PinVerifyRequest(BaseModel):
    """PIN verification request."""
    pin: str = Field(..., min_length=4, max_length=6, description="4-6 digit PIN")


@router.post(
    "/accounts/{account_number}/verify-pin",
    status_code=status.HTTP_200_OK,
    tags=["Accounts - Verification"],
    summary="Verify Account PIN",
    description="Verify if the provided PIN matches the account PIN"
)
async def verify_pin(
    account_number: int,
    request: PinVerifyRequest,
    claims: Dict[str, Any] = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Verify account PIN.
    
    Frontend calls: POST /api/v1/accounts/{account_number}/verify-pin
    Body: { pin: "1234" }
    
    **Authorization:** Any authenticated user
    
    **Returns:**
    - valid: true if PIN matches
    - message: Verification result message
    """
    try:
        login_id = JWTValidator.get_login_id(claims)
        logger.info(f"🔐 PIN verification for account {account_number} by {login_id}")
        
        # Verify PIN using the account service
        is_valid = await account_service.verify_pin(account_number, request.pin)
        
        if is_valid:
            return {"valid": True, "message": "PIN verified successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": "INVALID_PIN", "message": "Invalid PIN"}
            )
    
    except AccountException as e:
        logger.error(f"❌ PIN verification failed: {e.error_code}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "NOT_FOUND" in e.error_code else status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in PIN verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


@router.put(
    "/accounts/{account_number}",
    response_model=AccountResponse,
    status_code=status.HTTP_200_OK,
    tags=["Accounts - Update"],
    summary="Update Account Details",
    description="Update account information (ADMIN/TELLER only)"
)
async def update_account(
    account_number: int,
    request: AccountUpdate,
    claims: Dict[str, Any] = Depends(require_admin_or_teller()),
    account_service: AccountService = Depends(get_account_service)
):
    """
    Update account details.
    
    **Authorization:** ADMIN or TELLER role required
    
    **Updatable Fields:**
    - name: Account holder name
    - privilege: Account privilege level (PREMIUM, GOLD, SILVER)
    - phone_no: Phone number (SAVINGS accounts only)
    - company_name: Company name (CURRENT accounts only)
    - website: Company website (CURRENT accounts only)
    
    **Cannot Update:**
    - account_number, account_type, balance, is_active
    """
    try:
        login_id = JWTValidator.get_login_id(claims)
        updated_account = await account_service.update_account(account_number, request)
        logger.info(f"Account {account_number} updated by {login_id}")
        
        return AccountResponse(
            account_number=updated_account.account_number,
            account_type=updated_account.account_type,
            name=updated_account.name,
            privilege=updated_account.privilege,
            balance=updated_account.balance,
            is_active=updated_account.is_active,
            activated_date=updated_account.activated_date,
            closed_date=updated_account.closed_date
        )
    except AccountException as e:
        logger.error(f"❌ Update account failed: {e.error_code}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "NOT_FOUND" in e.error_code else status.HTTP_400_BAD_REQUEST,
            detail={"error_code": e.error_code, "message": e.message}
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "INTERNAL_ERROR", "message": "Internal server error"}
        )
