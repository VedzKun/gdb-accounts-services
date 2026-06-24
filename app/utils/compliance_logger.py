"""
Compliance Logger Utility

Handles auditing requirements:
- Writing account details to a text file
- Logging encrypted sensitive data (Aadhar, PIN) to CSV
- Action logging

Author: GDB Architecture Team
"""

import os
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from app.utils.encryption import EncryptionManager

logger = logging.getLogger(__name__)

class ComplianceLogger:
    """Utility for compliance and audit logging."""
    
    def __init__(self):
        self.encryption = EncryptionManager()
        self.logs_dir = Path("logs/compliance")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.accounts_file = self.logs_dir / "created_accounts.txt"
        self.audit_csv = self.logs_dir / "audit_log.csv"
        
        # Initialize CSV if not exists
        if not self.audit_csv.exists():
            with open(self.audit_csv, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Account Number", "Action", "Encrypted_Aadhar", "Encrypted_PIN"])

    async def log_account_creation(self, account_number: int, account_data: Dict[str, Any], pin: str):
        """
        Implementation of requirements 15, 16, 17.
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 15. Store account information in a text file
            with open(self.accounts_file, "a") as f:
                f.write(f"[{timestamp}] New Account Created: {account_number}\n")
                f.write(f"Holder: {account_data.get('name')}\n")
                f.write(f"Type: {account_data.get('account_type')}\n")
                f.write("-" * 30 + "\n")
            
            # 16. Encrypt PIN and Aadhar, log in CSV
            # Note: We use the actual PIN/Aadhar before hashing/masking for the audit log
            encrypted_aadhar = self.encryption.encrypt_data(account_data.get("aadhar_number", "N/A"))
            encrypted_pin = self.encryption.encrypt_data(pin)
            
            with open(self.audit_csv, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp, 
                    account_number, 
                    "Acc created", 
                    encrypted_aadhar, 
                    encrypted_pin
                ])
                
            logger.info(f"✅ Compliance logs updated for account {account_number}")
            
        except Exception as e:
            logger.error(f"❌ Error in compliance logging: {e}")
            # We don't raise here to avoid failing account creation if logging fails
            # but in a real production system, this might be a critical failure.

compliance_logger = ComplianceLogger()
