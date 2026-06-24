"""
Reset Database Script for Accounts Service

This script will:
1. Drop the existing database completely
2. Call setup_db.py to recreate the database with the latest schema

Usage:
    python reset_db.py
"""

import asyncio
import sys
import logging
from pathlib import Path
import subprocess

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config.settings import settings
from app.config.logging import setup_logging
import asyncpg

# Setup logging
logger = setup_logging()


async def drop_database():
    """Drop the existing database completely."""
    
    logger.info("🔧 Starting database drop...")
    
    # Connection string for postgres admin user
    db_url = str(settings.database_url)
    
    # Extract connection details
    if "postgresql://" in db_url:
        # Parse: postgresql://user:password@host:port/database
        parts = db_url.replace("postgresql://", "").split("@")
        user_pass = parts[0].split(":")
        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ""
        
        host_port = parts[1].split("/")
        host = host_port[0].split(":")[0]
        port = int(host_port[0].split(":")[1]) if ":" in host_port[0] else 5432
        database = host_port[1]
    else:
        logger.error("❌ Invalid DATABASE_URL format")
        print("❌ Invalid DATABASE_URL format")
        return False
    
    try:
        print(f"📡 Connecting to PostgreSQL at {host}:{port}...")
        logger.info(f"Connecting to PostgreSQL at {host}:{port}...")
        
        # Connect to postgres database first
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"
        )
        
        print(f"✅ Connected to PostgreSQL")
        logger.info(f"✅ Connected to PostgreSQL")
        
        # Check if database exists
        db_exists = await conn.fetchval(
            f"SELECT 1 FROM pg_database WHERE datname = $1",
            database
        )
        
        if db_exists:
            # Drop the database if it exists
            print(f"🗑️  Dropping existing database '{database}'...")
            logger.info(f"Dropping existing database '{database}'...")
            try:
                # Terminate all connections to the database
                await conn.execute(f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = '{database}'
                    AND pid <> pg_backend_pid();
                """)
                
                await conn.execute(f"DROP DATABASE IF EXISTS {database}")
                print(f"✅ Database '{database}' dropped successfully")
                logger.info(f"✅ Database '{database}' dropped successfully")
            except Exception as e:
                logger.error(f"Could not drop database: {e}")
                print(f"❌ Error: Could not drop database: {e}")
                await conn.close()
                return False
        else:
            print(f"ℹ️  Database '{database}' does not exist (nothing to drop)")
            logger.info(f"Database '{database}' does not exist")
        
        await conn.close()
        return True
        
    except asyncpg.exceptions.PostgresError as e:
        logger.error(f"Database error: {e}")
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_setup_db():
    """Run setup_db.py to recreate the database."""
    print("\n" + "=" * 60)
    print("📦 Running setup_db.py to recreate database...")
    print("=" * 60)
    print()
    
    logger.info("Running setup_db.py to recreate database...")
    
    try:
        # Get the path to setup_db.py
        setup_script = Path(__file__).parent / "setup_db.py"
        
        if not setup_script.exists():
            print(f"❌ setup_db.py not found at {setup_script}")
            logger.error(f"setup_db.py not found at {setup_script}")
            return False
        
        # Run setup_db.py
        result = subprocess.run(
            [sys.executable, str(setup_script)],
            cwd=str(Path(__file__).parent),
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("\n✅ Database recreated successfully!")
            logger.info("✅ Database recreated successfully!")
            return True
        else:
            print(f"\n❌ setup_db.py failed with return code {result.returncode}")
            logger.error(f"setup_db.py failed with return code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running setup_db.py: {e}")
        logger.error(f"Error running setup_db.py: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main entry point."""
    print("=" * 60)
    print("🏦 GDB Accounts Service - Database Reset")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This will DROP the entire database!")
    print("⚠️  All existing data will be permanently deleted!")
    print("=" * 60)
    print()
    
    logger.warning("=" * 60)
    logger.warning("🏦 GDB Accounts Service - Database Reset")
    logger.warning("⚠️  WARNING: This will DROP all existing data!")
    logger.warning("=" * 60)
    
    response = input("Type 'YES' to proceed with database reset: ")
    
    if response.upper() != "YES":
        print("❌ Reset cancelled.")
        logger.info("Reset cancelled by user")
        sys.exit(0)
    
    print()
    logger.info("Reset confirmed by user - proceeding...")
    
    # Step 1: Drop the database
    drop_success = await drop_database()
    
    if not drop_success:
        print("\n❌ Failed to drop database. Aborting.")
        logger.error("❌ Failed to drop database. Aborting.")
        sys.exit(1)
    
    # Step 2: Run setup_db.py to recreate
    setup_success = run_setup_db()
    
    print()
    if setup_success:
        print("=" * 60)
        print("✅ Database reset completed successfully!")
        print("=" * 60)
        logger.info("✅ Database reset completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Start the Aadhar service: uvicorn app.main:app --reload --port 8005")
        print("   2. Start the Accounts service: uvicorn app.main:app --reload --port 8002")
        print("   3. Create a new savings account with valid Aadhar number")
        print("\n💡 Valid Aadhar numbers: 123456789012, 234567890123, etc.")
        sys.exit(0)
    else:
        print("=" * 60)
        print("❌ Database reset failed. Check the errors above.")
        print("=" * 60)
        logger.error("❌ Database reset failed.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

