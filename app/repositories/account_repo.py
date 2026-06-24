"""
Accounts Service - Account Repository

Data access layer for account operations using raw SQL.
No ORM - pure asyncpg.

Author: GDB Architecture Team
"""

import logging
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
import asyncpg

from app.database.db import get_db
from app.exceptions.account_exceptions import (
    DatabaseError,
    AccountNotFoundError,
    DuplicateConstraintError
)
from app.models.account import (
    AccountDetailsResponse,
    SavingsAccountCreate,
    CurrentAccountCreate,
    AccountUpdate
)
from app.utils.helpers import AccountNumberGenerator

logger = logging.getLogger(__name__)


class AccountRepository:
    """
    Repository for account data access.
    
    Provides methods for CRUD operations on accounts.
    Uses raw SQL with asyncpg for type safety.
    """
    
    def __init__(self):
        """Initialize repository."""
        self.db = get_db()
    
    async def create_savings_account(self, account: SavingsAccountCreate, pin_hash: str) -> int:
        """
        Create a new savings account.
        
        Args:
            account: SavingsAccountCreate model
            pin_hash: Hashed PIN
            
        Returns:
            Account number (auto-generated)
            
        Raises:
            DuplicateConstraintError: If Aadhar number already exists
            DatabaseError: On database error
        """
        try:
            async with self.db.transaction() as conn:
                # Check for duplicate Aadhar number BEFORE generating account number
                existing = await conn.fetchval("""
                    SELECT account_number FROM savings_account_details 
                    WHERE aadhar_number = $1
                """, account.aadhar_number)
                
                if existing:
                    raise DuplicateConstraintError("aadhar_number")
                
                # Parse date_of_birth from string to date object
                dob = datetime.strptime(account.date_of_birth, "%Y-%m-%d").date()
                
                # Generate account number from sequence (starts at 1000)
                account_number = await conn.fetchval(
                    "SELECT nextval('account_number_seq')"
                )
                
                # Validate account number format
                if not AccountNumberGenerator.is_valid_account_number(account_number):
                    raise DatabaseError(f"Invalid account number generated: {account_number}")
                
                # Insert into accounts table with explicit account_number
                await conn.execute("""
                    INSERT INTO accounts 
                    (account_number, account_type, name, pin_hash, balance, privilege, is_active, activated_date, bank_name, bank_branch, ifsc_code)
                    VALUES ($1, $2, $3, $4, $5, $6, TRUE, CURRENT_TIMESTAMP, $7, $8, $9)
                """, account_number, "SAVINGS", account.name, pin_hash, account.initial_balance, account.privilege, 
                   account.bank_name, account.bank_branch, account.ifsc_code)
                
                # Insert into savings_account_details table
                await conn.execute("""
                    INSERT INTO savings_account_details 
                    (account_number, date_of_birth, gender, phone_no, aadhar_number)
                    VALUES ($1, $2, $3, $4, $5)
                """, account_number, dob, account.gender, account.phone_no, account.aadhar_number)
                
                logger.info(f"✅ Savings account created: {account_number}")
                return account_number
                
        except DuplicateConstraintError:
            raise
        except asyncpg.UniqueViolationError as e:
            if "aadhar" in str(e).lower():
                raise DuplicateConstraintError("aadhar_number")
            raise DatabaseError(str(e))
        except asyncpg.IntegrityConstraintViolationError as e:
            raise DatabaseError(str(e))
        except Exception as e:
            logger.error(f"❌ Error creating savings account: {e}")
            raise DatabaseError(str(e))
    
    async def create_current_account(self, account: CurrentAccountCreate, pin_hash: str) -> int:
        """
        Create a new current account.
        
        Args:
            account: CurrentAccountCreate model
            pin_hash: Hashed PIN
            
        Returns:
            Account number (auto-generated)
            
        Raises:
            DuplicateConstraintError: If registration_no exists
            DatabaseError: On database error
        """
        try:
            async with self.db.transaction() as conn:
                # Check for duplicate registration_no BEFORE generating account number
                existing = await conn.fetchval("""
                    SELECT account_number FROM current_account_details 
                    WHERE registration_no = $1
                """, account.registration_no)
                
                if existing:
                    raise DuplicateConstraintError("registration_no")
                
                # Generate account number from sequence (starts at 1000)
                account_number = await conn.fetchval(
                    "SELECT nextval('account_number_seq')"
                )
                
                # Validate account number format
                if not AccountNumberGenerator.is_valid_account_number(account_number):
                    raise DatabaseError(f"Invalid account number generated: {account_number}")
                
                # Insert into accounts table with explicit account_number
                await conn.execute("""
                    INSERT INTO accounts 
                    (account_number, account_type, name, pin_hash, balance, privilege, is_active, activated_date, bank_name, bank_branch, ifsc_code)
                    VALUES ($1, $2, $3, $4, $5, $6, TRUE, CURRENT_TIMESTAMP, $7, $8, $9)
                """, account_number, "CURRENT", account.name, pin_hash, 0.00, account.privilege,
                   account.bank_name, account.bank_branch, account.ifsc_code)
                
                # Insert into current_account_details table
                await conn.execute("""
                    INSERT INTO current_account_details 
                    (account_number, company_name, website, registration_no)
                    VALUES ($1, $2, $3, $4)
                """, account_number, account.company_name, account.website, account.registration_no)
                
                logger.info(f"✅ Current account created: {account_number}")
                return account_number
                
        except DuplicateConstraintError:
            raise
        except asyncpg.UniqueViolationError as e:
            if "registration_no" in str(e):
                raise DuplicateConstraintError("registration_no")
            raise DatabaseError(str(e))
        except asyncpg.IntegrityConstraintViolationError as e:
            raise DatabaseError(str(e))
        except Exception as e:
            logger.error(f"❌ Error creating current account: {e}")
            raise DatabaseError(str(e))
    
    async def get_account(self, account_number: int) -> Optional[dict]:
        """
        Fetch account details with type-specific information.
        
        Args:
            account_number: Account number to fetch
            
        Returns:
            Dictionary with full account details or None if not found
            
        Raises:
            DatabaseError: On database error
        """
        try:
            # First get base account info
            row = await self.db.fetch_one("""
                SELECT 
                    account_number, account_type, name, balance::numeric(15,2) as balance, 
                    privilege, is_active, activated_date, closed_date,
                    bank_name, bank_branch, ifsc_code
                FROM accounts
                WHERE account_number = $1
            """, account_number)
            
            if not row:
                return None
            
            # Explicitly convert balance to float
            balance_value = row['balance']
            if balance_value is not None:
                if isinstance(balance_value, Decimal):
                    balance_value = float(balance_value)
                elif isinstance(balance_value, str):
                    balance_value = float(balance_value)
                else:
                    balance_value = float(balance_value)
            else:
                balance_value = 0.0
            
            # Build base response
            result = {
                'account_number': row['account_number'],
                'account_type': row['account_type'],
                'name': row['name'],
                'balance': balance_value,
                'privilege': row['privilege'],
                'is_active': row['is_active'],
                'activated_date': row['activated_date'],
                'closed_date': row['closed_date'],
                'bank_name': row['bank_name'],
                'bank_branch': row['bank_branch'],
                'ifsc_code': row['ifsc_code']
            }
            
            # Fetch type-specific details
            if row['account_type'] == 'SAVINGS':
                savings_row = await self.db.fetch_one("""
                    SELECT date_of_birth, gender, phone_no, aadhar_number
                    FROM savings_account_details
                    WHERE account_number = $1
                """, account_number)
                if savings_row:
                    result['date_of_birth'] = str(savings_row['date_of_birth']) if savings_row['date_of_birth'] else None
                    result['gender'] = savings_row['gender']
                    result['phone_no'] = savings_row['phone_no']
                    result['aadhar_number'] = savings_row['aadhar_number']
            elif row['account_type'] == 'CURRENT':
                current_row = await self.db.fetch_one("""
                    SELECT company_name, registration_no, website
                    FROM current_account_details
                    WHERE account_number = $1
                """, account_number)
                if current_row:
                    result['company_name'] = current_row['company_name']
                    result['registration_no'] = current_row['registration_no']
                    result['website'] = current_row['website']
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error fetching account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    async def get_all_accounts(self, account_type: str | None = None) -> List[AccountDetailsResponse]:
        """
        Fetch all accounts, optionally filtered by account type.
        
        Args:
            account_type: Optional filter for account type (SAVINGS or CURRENT)
        
        Returns:
            List of AccountDetailsResponse
            
        Raises:
            DatabaseError: On database error
        """
        try:
            # Build query with optional WHERE clause
            query = """
                SELECT 
                    account_number, account_type, name, balance::numeric(15,2) as balance, 
                    privilege, is_active, activated_date, closed_date,
                    bank_name, bank_branch, ifsc_code
                FROM accounts
            """
            
            params = []
            if account_type:
                query += " WHERE account_type = $1"
                params.append(account_type)
            
            query += " ORDER BY account_number DESC"
            
            rows = await self.db.fetch_all(query, *params)
            
            if not rows:
                return []
            
            accounts = []
            for row in rows:
                # Explicitly convert balance to float
                balance_value = row['balance']
                if balance_value is not None:
                    if isinstance(balance_value, Decimal):
                        balance_value = float(balance_value)
                    elif isinstance(balance_value, str):
                        balance_value = float(balance_value)
                    else:
                        balance_value = float(balance_value)
                else:
                    balance_value = 0.0
                
                accounts.append(AccountDetailsResponse(
                    account_number=row['account_number'],
                    account_type=row['account_type'],
                    name=row['name'],
                    balance=balance_value,
                    privilege=row['privilege'],
                    is_active=row['is_active'],
                    activated_date=row['activated_date'],
                    closed_date=row['closed_date'],
                    bank_name=row['bank_name'],
                    bank_branch=row['bank_branch'],
                    ifsc_code=row['ifsc_code']
                ))
            
            logger.info(f"✅ Fetched {len(accounts)} accounts from database")
            return accounts
        
        except Exception as e:
            logger.error(f"❌ Error fetching all accounts: {e}")
            raise DatabaseError(str(e))
    
    async def update_account(self, account_number: int, update_data: dict, account_type: str) -> Optional[AccountDetailsResponse]:
        """
        Update account details.
        
        Args:
            account_number: Account number
            update_data: Dictionary of fields to update
            account_type: SAVINGS or CURRENT
            
        Returns:
            Updated AccountDetailsResponse
            
        Raises:
            DatabaseError: On database error
        """
        try:
            async with self.db.transaction() as conn:
                # 1. Update common fields in accounts table
                updates = []
                values = []
                param_count = 1

                if 'name' in update_data:
                    updates.append(f"name = ${param_count}")
                    values.append(update_data['name'])
                    param_count += 1
                
                if 'privilege' in update_data:
                    updates.append(f"privilege = ${param_count}")
                    values.append(update_data['privilege'])
                    param_count += 1
                
                if updates:
                    updates.append(f"updated_at = CURRENT_TIMESTAMP")
                    values.append(account_number)
                    
                    query = f"""
                        UPDATE accounts
                        SET {', '.join(updates)}
                        WHERE account_number = ${param_count}
                    """
                    await conn.execute(query, *values)

                # 2. Update type-specific fields
                if account_type == "SAVINGS":
                    savings_updates = []
                    savings_values = []
                    s_param_count = 1
                    
                    if 'phone_no' in update_data:
                        savings_updates.append(f"phone_no = ${s_param_count}")
                        savings_values.append(update_data['phone_no'])
                        s_param_count += 1
                        
                    if savings_updates:
                        savings_values.append(account_number)
                        s_query = f"""
                            UPDATE savings_account_details
                            SET {', '.join(savings_updates)}
                            WHERE account_number = ${s_param_count}
                        """
                        await conn.execute(s_query, *savings_values)
                        
                elif account_type == "CURRENT":
                    current_updates = []
                    current_values = []
                    c_param_count = 1
                    
                    if 'company_name' in update_data:
                        current_updates.append(f"company_name = ${c_param_count}")
                        current_values.append(update_data['company_name'])
                        c_param_count += 1
                        
                    if 'website' in update_data:
                        current_updates.append(f"website = ${c_param_count}")
                        current_values.append(update_data['website'])
                        c_param_count += 1
                        
                    if current_updates:
                        current_values.append(account_number)
                        c_query = f"""
                            UPDATE current_account_details
                            SET {', '.join(current_updates)}
                            WHERE account_number = ${c_param_count}
                        """
                        await conn.execute(c_query, *current_values)

                logger.info(f"✅ Account {account_number} updated successfully")
                
            # Return updated account
            return await self.get_account(account_number)
            
        except Exception as e:
            logger.error(f"❌ Error updating account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    async def get_account_balance(self, account_number: int) -> Optional[float]:
        """
        Get account balance.
        
        Args:
            account_number: Account number
            
        Returns:
            Balance or None if account doesn't exist
            
        Raises:
            DatabaseError: On database error
        """
        try:
            balance = await self.db.fetch_val("""
                SELECT balance FROM accounts WHERE account_number = $1
            """, account_number)
            
            return float(balance) if balance is not None else None
            
        except Exception as e:
            logger.error(f"❌ Error fetching balance for {account_number}: {e}")
            raise DatabaseError(str(e))
    
    async def debit_account(
        self,
        account_number: int,
        amount: float
    ) -> bool:
        """
        Debit amount from account (WITHDRAW/TRANSFER FROM).
        
        Args:
            account_number: Account to debit
            amount: Amount to debit (positive value)
            
        Returns:
            True if successful
            
        Raises:
            DatabaseError: On database error
        """
        try:
            async with self.db.transaction() as conn:
                # Perform debit with check
                result = await conn.execute("""
                    UPDATE accounts
                    SET balance = balance - $1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE account_number = $2 
                    AND balance >= $1
                    AND is_active = TRUE
                """, amount, account_number)
                
                if result == "UPDATE 0":
                    logger.warning(f"⚠️ Debit failed for {account_number}: insufficient balance or inactive")
                    return False
                
                logger.info(f"✅ Debit successful: {account_number}, Amount: ₹{amount}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error debiting account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    async def credit_account(
        self,
        account_number: int,
        amount: float
    ) -> bool:
        """
        Credit amount to account (DEPOSIT/TRANSFER TO).
        
        Args:
            account_number: Account to credit
            amount: Amount to credit (positive value)
            
        Returns:
            True if successful
            
        Raises:
            DatabaseError: On database error
        """
        try:
            async with self.db.transaction() as conn:
                # Perform credit
                result = await conn.execute("""
                    UPDATE accounts
                    SET balance = balance + $1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE account_number = $2
                    AND is_active = TRUE
                """, amount, account_number)
                
                if result == "UPDATE 0":
                    logger.warning(f"⚠️ Credit failed for {account_number}: account not found or inactive")
                    return False
                
                logger.info(f"✅ Credit successful: {account_number}, Amount: ₹{amount}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error crediting account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    
    async def activate_account(self, account_number: int) -> bool:
        """
        Activate an account.
        
        Args:
            account_number: Account to activate
            
        Returns:
            True if activated, False if not found
            
        Raises:
            DatabaseError: On database error
        """
        try:
            result = await self.db.execute("""
                UPDATE accounts
                SET is_active = TRUE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE account_number = $1
            """, account_number)
            
            if result == "UPDATE 0":
                return False
            
            logger.info(f"✅ Account activated: {account_number}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error activating account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    async def inactivate_account(self, account_number: int) -> bool:
        """
        Inactivate an account.
        
        Args:
            account_number: Account to inactivate
            
        Returns:
            True if inactivated, False if not found
            
        Raises:
            DatabaseError: On database error
        """
        try:
            result = await self.db.execute("""
                UPDATE accounts
                SET is_active = FALSE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE account_number = $1
            """, account_number)
            
            if result == "UPDATE 0":
                return False
            
            logger.info(f"✅ Account inactivated: {account_number}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inactivating account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    async def close_account(self, account_number: int) -> bool:
        """
        Close an account (soft delete).
        
        Args:
            account_number: Account to close
            
        Returns:
            True if closed, False if not found
            
        Raises:
            DatabaseError: On database error
        """
        try:
            result = await self.db.execute("""
                UPDATE accounts
                SET is_active = FALSE,
                    closed_date = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE account_number = $1
            """, account_number)
            
            if result == "UPDATE 0":
                return False
            
            logger.info(f"✅ Account closed: {account_number}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error closing account {account_number}: {e}")
            raise DatabaseError(str(e))
    
    async def get_pin_hash(self, account_number: int) -> Optional[str]:
        """
        Get PIN hash for an account (for verification).
        
        Args:
            account_number: Account number
            
        Returns:
            PIN hash or None
            
        Raises:
            DatabaseError: On database error
        """
        try:
            return await self.db.fetch_val("""
                SELECT pin_hash FROM accounts WHERE account_number = $1
            """, account_number)
            
        except Exception as e:
            logger.error(f"❌ Error fetching PIN hash: {e}")
            raise DatabaseError(str(e))

    async def check_aadhar_has_active_account(self, aadhar_number: str) -> bool:
        """
        Check if an Aadhar number already has an active savings account.
        
        Args:
            aadhar_number: 12-digit Aadhar number
            
        Returns:
            True if an active account exists
        """
        try:
            # Join accounts and savings_account_details to check for active accounts
            exists = await self.db.fetch_val("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM accounts a
                    JOIN savings_account_details s ON a.account_number = s.account_number
                    WHERE s.aadhar_number = $1 AND a.is_active = TRUE AND a.closed_date IS NULL
                )
            """, aadhar_number)
            return exists
        except Exception as e:
            logger.error(f"❌ Error checking active Aadhar account: {e}")
            raise DatabaseError(str(e))
