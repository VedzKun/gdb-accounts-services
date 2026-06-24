"""
Accounts Service - Configuration Settings

This module provides environment-based configuration for the Accounts Service.
Follows 12-factor app principles with environment variables.

Author: GDB Architecture Team
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Application Info
    APP_NAME: str = "GDB-Accounts-Service"
    TITLE: str = "GDB Accounts Service"
    DESCRIPTION: str = "Microservice for managing bank accounts"
    APP_VERSION: str = "1.0.0"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    # Converting int to str allows pydantic to take in any value and not just pure int.
    # in case conversion fails we fall back to the default value
    PORT: str = "8001"
    
    # Database Settings
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/gdb_accounts_db"
    MIN_DB_POOL_SIZE: int = 5
    MAX_DB_POOL_SIZE: int = 20
    
    # Security Settings
    PIN_ENCRYPTION_KEY: str = "your-secret-encryption-key"
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DISABLE_AUTH: bool = False
    
    # Inter-Service URLs (StandardizedPlural and LegacySingular)
    ACCOUNTS_SERVICE_URL: str = "http://localhost:8001"
    ACCOUNT_SERVICE_URL: str = "http://localhost:8001"
    
    TRANSACTIONS_SERVICE_URL: str = "http://localhost:8002"
    TRANSACTION_SERVICE_URL: str = "http://localhost:8002"
    
    USERS_SERVICE_URL: str = "http://localhost:8003"
    USER_SERVICE_URL: str = "http://localhost:8003"
    
    AUTH_SERVICE_URL: str = "http://localhost:8004"
    AADHAR_SERVICE_URL: str = "http://localhost:8005"
    COMPANY_SERVICE_URL: str = "http://localhost:8006"
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8007"
    PAYMENT_GATEWAY_SERVICE_URL: str = "http://localhost:8008"
    
    # Integration Settings
    ACCOUNT_SERVICE_TIMEOUT: int = 10
    
    # API prefix
    API_PREFIX: str = "/api/v1"
    
    # CORS - Allow frontend origins
    CORS_ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8001", "http://localhost:8002", "http://localhost:8003", "http://localhost:8004", "*"]
    
    # Logging
    LOG_LEVEL: str = "INFO"

    # Compatibility Aliases (Lowercase for existing code)
    @property
    def app_name(self) -> str: return self.APP_NAME
    @property
    def app_version(self) -> str: return self.APP_VERSION
    @property
    def host(self) -> str: return self.HOST
    @property
    def port(self) -> int:
        port_env = os.getenv("PORT")
        if not port_env:
            try:
                return int(self.PORT)
            except ValueError:
                return 8001
        try:
            return int(port_env)
        except ValueError:
            try:
                return int(self.model_fields['PORT'].default)
            except (KeyError, ValueError, TypeError):
                return 8001
    @property
    def database_url(self) -> str: return self.DATABASE_URL
    @property
    def min_db_pool_size(self) -> int: return self.MIN_DB_POOL_SIZE
    @property
    def max_db_pool_size(self) -> int: return self.MAX_DB_POOL_SIZE
    @property
    def jwt_secret_key(self) -> str: return self.JWT_SECRET_KEY
    @property
    def jwt_algorithm(self) -> str: return self.JWT_ALGORITHM
    @property
    def api_prefix(self) -> str: return self.API_PREFIX
    @property
    def log_level(self) -> str: return self.LOG_LEVEL
    @property
    def environment(self) -> str: return self.ENVIRONMENT
    @property
    def debug(self) -> bool: return self.DEBUG
    @property
    def disable_auth(self) -> bool: return self.DISABLE_AUTH
    @property
    def account_service_url(self) -> str: return self.ACCOUNTS_SERVICE_URL

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

settings = Settings()

# Schema configuration for multi-tenant database
SCHEMA_NAME = "accounts_service"

# Update search_path for PostgreSQL
async def set_schema_search_path(connection):
    """Set the search path to use the correct schema."""
    await connection.execute(f"SET search_path TO accounts_service, public")
