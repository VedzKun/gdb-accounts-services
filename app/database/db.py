"""
Accounts Service - Database Connection Management

This module provides async database connection pooling using asyncpg.
Raw SQL operations only - no ORM.

Author: GDB Architecture Team
"""

import asyncpg
from typing import Optional
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages asyncpg connection pool for PostgreSQL.
    
    Provides async context managers for database operations.
    Ensures proper resource cleanup and connection pooling.
    """
    
    def __init__(self, database_url: str, min_size: int = 5, max_size: int = 20):
        """
        Initialize database manager.
        
        Args:
            database_url: PostgreSQL connection URL
            min_size: Minimum pool size
            max_size: Maximum pool size
        """
        self.database_url = database_url
        self.min_size = min_size
        self.max_size = max_size
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        """
        Create connection pool.
        
        Raises:
            asyncpg.PostgresError: If connection fails
        """
        try:
            self.pool = await asyncpg.create_pool(dsn=self.database_url, setup=set_schema_search_path,
                min_size=self.min_size,
                max_size=self.max_size,
                timeout=10,
                command_timeout=10
            )
            logger.info("✅ Database connection pool established")
        except asyncpg.PostgresError as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    async def disconnect(self) -> None:
        """
        Close all connections in pool.
        """
        if self.pool:
            await self.pool.close()
            logger.info("✅ Database connection pool closed")
    
    @asynccontextmanager
    async def transaction(self):
        """
        Async context manager for transaction management.
        
        Yields:
            asyncpg.Connection: Database connection with active transaction
            
        Usage:
            async with db_manager.transaction() as conn:
                await conn.execute("INSERT INTO ...")
        """
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                yield conn
    
    @asynccontextmanager
    async def get_connection(self):
        """
        Async context manager to get a single connection.
        
        Yields:
            asyncpg.Connection: Database connection
        """
        async with self.pool.acquire() as conn:
            yield conn
    
    async def execute(self, query: str, *args) -> str:
        """
        Execute a query (INSERT, UPDATE, DELETE).
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            Command completion status
        """
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch_one(self, query: str, *args) -> Optional[asyncpg.Record]:
        """
        Fetch a single row.
        
        Args:
            query: SQL SELECT query
            *args: Query parameters
            
        Returns:
            Single row as asyncpg.Record or None
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetch_all(self, query: str, *args) -> list:
        """
        Fetch multiple rows.
        
        Args:
            query: SQL SELECT query
            *args: Query parameters
            
        Returns:
            List of asyncpg.Record objects
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetch_val(self, query: str, *args):
        """
        Fetch a single scalar value.
        
        Args:
            query: SQL query returning single value
            *args: Query parameters
            
        Returns:
            Single scalar value
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)


# Global database manager instance
db: Optional[DatabaseManager] = None


async def initialize_db(database_url: str, min_size: int = 5, max_size: int = 20) -> DatabaseManager:
    """
    Initialize global database manager.
    Also handles automatic database creation, schema execution, and seeding.
    
    Args:
        database_url: PostgreSQL connection URL
        min_size: Minimum pool size
        max_size: Maximum pool size
        
    Returns:
        DatabaseManager instance
    """
    global db
    from pathlib import Path
    
    # Extract connection details for checking/creating database
    db_host = "localhost"
    db_port = 5432
    db_user = "postgres"
    db_password = ""
    db_name = "gdb_accounts_db"
    
    if "postgresql://" in database_url:
        try:
            parts = database_url.replace("postgresql://", "").split("@")
            user_pass = parts[0].split(":")
            db_user = user_pass[0]
            db_password = user_pass[1] if len(user_pass) > 1 else ""
            
            host_port = parts[1].split("/")
            db_host = host_port[0].split(":")[0]
            db_port = int(host_port[0].split(":")[1]) if ":" in host_port[0] else 5432
            db_name = host_port[1]
        except Exception as e:
            logger.error(f"Failed to parse database_url {database_url}: {e}")

    # 1. Connect to postgres DB to verify/create target DB
    try:
        logger.info(f"Checking if database {db_name} exists...")
        temp_conn = await asyncpg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database="postgres"
        )
        db_exists = await temp_conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            db_name
        )
        if not db_exists:
            logger.info(f"📦 Creating database: {db_name}")
            await temp_conn.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"✅ Database created: {db_name}")
        else:
            logger.info(f"✅ Database already exists: {db_name}")
        await temp_conn.close()
    except Exception as e:
        logger.error(f"⚠️ Error verifying/creating database {db_name}: {e}")

    db = DatabaseManager(database_url, min_size, max_size)
    await db.connect()
    logger.info("✅ Database pool established")

    # 2. Check if tables exist, run schema, and seed
    try:
        async with db.get_connection() as conn:
            accounts_exists = await conn.fetchval(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = current_schema() AND table_name = 'accounts')"
            )
            if not accounts_exists:
                logger.info("📋 Core table 'accounts' does not exist. Running accounts_schema.sql...")
                schema_path = Path(__file__).parent / "accounts_schema.sql"
                if schema_path.exists():
                    with open(schema_path, "r", encoding="utf-8") as f:
                        schema_sql = f.read()
                    
                    # Execute schema (it may contain custom type creations)
                    # We wrap this to handle DuplicateObjectError in case the types already exist
                    try:
                        await conn.execute(schema_sql)
                        logger.info("✅ Schema executed successfully")
                    except asyncpg.exceptions.DuplicateObjectError as doe:
                        logger.warning(f"⚠️ Duplicate object during schema execution: {doe}. Trying to execute statements individually...")
                        # Fallback: split schema by semicolon and execute statement by statement
                        for stmt in schema_sql.split(";"):
                            stmt_strip = stmt.strip()
                            if stmt_strip:
                                try:
                                    await conn.execute(stmt_strip)
                                except Exception as stmt_err:
                                    # Ignore duplicate object/relation errors, raise other serious errors
                                    if "already exists" not in str(stmt_err):
                                        logger.error(f"Error executing statement: {stmt_strip}. Error: {stmt_err}")
                else:
                    logger.error(f"❌ Schema file not found at {schema_path}")
            
            # Ensure accounts_audit table exists as well
            audit_exists = await conn.fetchval(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = current_schema() AND table_name = 'accounts_audit')"
            )
            if not audit_exists and accounts_exists:
                logger.info("📋 Creating accounts_audit table and index...")
                await conn.execute("""
                    CREATE TABLE accounts_audit (
                        id BIGSERIAL PRIMARY KEY,
                        account_number BIGINT NOT NULL REFERENCES accounts(account_number) ON DELETE CASCADE,
                        action_type VARCHAR(50) NOT NULL,
                        changed_by VARCHAR(255) NOT NULL,
                        changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE INDEX idx_accounts_audit_lookup ON accounts_audit(account_number, changed_at);
                """)
                logger.info("✅ accounts_audit table and index created successfully")

            # Check if any accounts exist
            acc_count = await conn.fetchval("SELECT COUNT(*) FROM accounts")
            if acc_count == 0:
                logger.info("🌱 Seeding default accounts...")
                import bcrypt
                
                # Default PIN hash (PIN: 1234)
                pin_hash = bcrypt.hashpw("1234".encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
                
                # Seed John Doe Savings
                await conn.execute(
                    """
                    INSERT INTO accounts (account_number, account_type, name, pin_hash, balance, privilege, bank_name, bank_branch, ifsc_code, is_active)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    """,
                    1001, "SAVINGS", "John Doe", pin_hash, 50000.00, "GOLD", "Global Digital Bank", "Main Branch", "GDB0000001", True
                )
                
                await conn.execute(
                    """
                    INSERT INTO savings_account_details (account_number, date_of_birth, gender, phone_no, aadhar_number)
                    VALUES ($1, '1990-01-01'::date, $2::gender_enum, $3, $4)
                    """,
                    1001, "Male", "9876543210", "123456780012"
                )
                
                # Seed Admin Current
                await conn.execute(
                    """
                    INSERT INTO accounts (account_number, account_type, name, pin_hash, balance, privilege, bank_name, bank_branch, ifsc_code, is_active)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    """,
                    1002, "CURRENT", "System Admin", pin_hash, 250000.00, "PREMIUM", "Global Digital Bank", "Main Branch", "GDB0000001", True
                )
                
                await conn.execute(
                    """
                    INSERT INTO current_account_details (account_number, company_name, website, registration_no)
                    VALUES ($1, $2, $3, $4)
                    """,
                    1002, "Admin Tech Corp", "admintech.com", "U12345MH2020PTC123456"
                )
                
                # Set sequence to 1005 so next accounts created start from there
                await conn.execute("SELECT setval('account_number_seq', 1005)")
                logger.info("✅ Seeded default accounts successfully")
    except Exception as e:
        logger.error(f"❌ Error during accounts schema verification/seeding: {e}")
        raise
    return db


async def close_db() -> None:
    """Close database connections."""
    global db
    if db:
        await db.disconnect()
        db = None


def get_db() -> DatabaseManager:
    """
    Get current database manager instance.
    
    Returns:
        DatabaseManager instance
        
    Raises:
        RuntimeError: If database not initialized
    """
    if db is None:
        raise RuntimeError("Database not initialized. Call initialize_db() first.")
    return db

# Schema configuration for multi-tenant database
SCHEMA_NAME = "accounts_service"

# Update search_path for PostgreSQL
async def set_schema_search_path(connection):
    """Set the search path to use the correct schema."""
    await connection.execute(f"SET search_path TO accounts_service, public")
