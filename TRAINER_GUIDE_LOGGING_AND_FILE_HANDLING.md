# Trainer Guide: Logging and File Handling in Banking Applications

## Table of Contents
1. [Why Logging Matters in Banking](#why-logging-matters)
2. [Types of Logging in Our System](#types-of-logging)
3. [File Handling Implementation](#file-handling-implementation)
4. [Security Considerations](#security-considerations)
5. [Common Questions & Answers](#common-questions)
6. [Hands-On Demonstrations](#hands-on-demonstrations)

---

## Why Logging Matters in Banking

### Real-World Context
**Ask trainees:** "What happens if a customer says they deposited ₹50,000 but the system shows ₹0?"

**Answer:** Without proper logging, you cannot:
- Prove what actually happened
- Debug the issue
- Comply with RBI regulations
- Protect the bank from fraud claims
- Audit transactions for tax purposes

### Regulatory Requirements
In India, RBI (Reserve Bank of India) mandates:
- **7-year retention** of all financial transaction records
- **Audit trails** for every account operation
- **Tamper-proof logs** that cannot be modified
- **Encryption** of sensitive customer data

### Our Implementation Philosophy
We use **dual logging**:
1. **Human-Readable Logs** (Text files) - For quick review by staff
2. **Machine-Readable Logs** (CSV files) - For automated audits and compliance

---

## Types of Logging in Our System

### 1. Application Logs (Python `logging` module)
**Location:** Console output and application log files
**Purpose:** Debugging, monitoring, error tracking

```python
import logging
logger = logging.getLogger(__name__)

# Different log levels
logger.debug("Detailed information for debugging")
logger.info("✅ Account created: 1001")
logger.warning("⚠️ Unusual activity detected")
logger.error("❌ Database connection failed")
logger.critical("🚨 System shutdown required")
```

**When to use each level:**
- `DEBUG`: Development only, very detailed
- `INFO`: Normal operations (account created, transaction completed)
- `WARNING`: Something unusual but not breaking (retry attempts, slow response)
- `ERROR`: Something failed but system continues (validation error, API timeout)
- `CRITICAL`: System-level failure (database down, service crashed)

### 2. Compliance Logs (Our Custom Implementation)
**Location:** `logs/compliance/` directory
**Purpose:** Regulatory compliance, audit trail, legal evidence

#### File Structure:
```
logs/
└── compliance/
    ├── created_accounts.txt    # Human-readable account log
    └── audit_log.csv           # Machine-readable audit trail
```

---

## File Handling Implementation

### Code Walkthrough: `compliance_logger.py`

Let's break down the implementation step by step:

#### Step 1: Initialize the Logger
```python
class ComplianceLogger:
    def __init__(self):
        # Create encryption manager for sensitive data
        self.encryption = EncryptionManager()
        
        # Define log directory
        self.logs_dir = Path("logs/compliance")
        
        # Create directory if it doesn't exist
        # parents=True: Create parent directories too
        # exist_ok=True: Don't error if already exists
        self.logs_dir.mkdir(parents=True, exist_ok=True)
```

**Explain to trainees:**
- `Path()` is from Python's `pathlib` - modern way to handle file paths
- `mkdir(parents=True)` creates all intermediate directories
- `exist_ok=True` prevents errors if the folder already exists

#### Step 2: Initialize CSV File with Headers
```python
        self.audit_csv = self.logs_dir / "audit_log.csv"
        
        # Create CSV with headers if it doesn't exist
        if not self.audit_csv.exists():
            with open(self.audit_csv, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp", 
                    "Account Number", 
                    "Action", 
                    "Encrypted_Aadhar", 
                    "Encrypted_PIN"
                ])
```

**Key Points:**
- `newline=""` prevents extra blank lines in CSV on Windows
- Headers are written only once when file is created
- CSV format allows easy import into Excel, databases, or analytics tools

#### Step 3: Log Account Creation
```python
async def log_account_creation(self, account_number: int, account_data: Dict, pin: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Write to human-readable text file
    with open(self.accounts_file, "a") as f:  # "a" = append mode
        f.write(f"[{timestamp}] New Account Created: {account_number}\n")
        f.write(f"Holder: {account_data.get('name')}\n")
        f.write(f"Type: {account_data.get('account_type')}\n")
        f.write("-" * 30 + "\n")
    
    # 2. Encrypt sensitive data
    encrypted_aadhar = self.encryption.encrypt_data(
        account_data.get("aadhar_number", "N/A")
    )
    encrypted_pin = self.encryption.encrypt_data(pin)
    
    # 3. Write to CSV audit log
    with open(self.audit_csv, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp,
            account_number,
            "Account Created",
            encrypted_aadhar,
            encrypted_pin
        ])
```

---

## Security Considerations

### Why We Encrypt in Logs

**Scenario Question for Trainees:**
"What if someone hacks into our server and steals the audit_log.csv file?"

**Answer:** 
- Without encryption: They get all Aadhar numbers and PINs in plain text
- With encryption: They get gibberish that's useless without the encryption key

### Encryption Example

**Plain Text:**
```
Aadhar: 123456789012
PIN: 1357
```

**Encrypted (Fernet):**
```
Aadhar: gAAAAABl8xK9vQz8... (128 characters of random-looking text)
PIN: gAAAAABl8xK9pLm4... (128 characters of random-looking text)
```

### Why We Mask Aadhar in API Responses

**Before Masking:** `123456789012`
**After Masking:** `********9012`

**Reason:** 
- Prevents shoulder surfing (someone looking at screen)
- Reduces data exposure in logs
- Complies with data minimization principle
- Still allows customer to verify their Aadhar

---

## Common Questions & Answers

### Q1: "Why use both text files AND CSV files?"

**Answer:**
- **Text files**: Easy for humans to read quickly
  - Bank staff can open in Notepad
  - Quick review during customer calls
  - No special software needed

- **CSV files**: Easy for computers to process
  - Import into Excel for analysis
  - Load into databases for queries
  - Automated compliance reports
  - Data analytics and fraud detection

**Analogy:** Like having both a paper receipt (text) and a digital transaction record (CSV).

### Q2: "What if the log file gets too big?"

**Answer:** In production, we implement **log rotation**:
```python
# Example: Rotate logs daily
audit_log_2026_01_22.csv
audit_log_2026_01_23.csv
audit_log_2026_01_24.csv
```

Or size-based rotation:
```python
audit_log_001.csv  (0-100MB)
audit_log_002.csv  (100-200MB)
audit_log_003.csv  (200-300MB)
```

### Q3: "Can we delete old logs to save space?"

**Answer:** **NO!** In banking:
- RBI requires 7-year retention
- Logs are legal evidence
- Needed for tax audits
- Required for dispute resolution

**Solution:** Archive old logs to cheaper storage (AWS S3 Glacier, tape backups)

### Q4: "What if logging fails? Does account creation fail too?"

**Answer:** Look at our code:
```python
try:
    # Log account creation
    await compliance_logger.log_account_creation(...)
except Exception as e:
    logger.error(f"❌ Error in compliance logging: {e}")
    # We don't raise here - account creation continues
```

**Design Decision:**
- Logging failure should NOT block account creation
- But we log the logging failure itself
- In production, trigger an alert to ops team

### Q5: "Why use `async` for file operations?"

**Answer:**
```python
async def log_account_creation(...):
    # File operations
```

**Explanation:**
- File I/O is slow (disk operations)
- `async` allows other operations to continue
- Prevents blocking the main application thread
- Better performance under high load

**Analogy:** Like a restaurant where the waiter doesn't stand at the kitchen waiting for food - they serve other tables while food is being prepared.

---

## Hands-On Demonstrations

### Demo 1: Show the Log Files

**Steps:**
1. Navigate to `logs/compliance/` directory
2. Open `created_accounts.txt` in Notepad
3. Open `audit_log.csv` in Excel

**Point out:**
- Timestamps are human-readable
- Text file shows account details clearly
- CSV has encrypted sensitive data
- CSV can be sorted, filtered in Excel

### Demo 2: Create a Test Account

**Steps:**
1. Run the accounts service
2. Create a new savings account via API
3. Immediately check the log files
4. Show how new entries appear

**Code to demonstrate:**
```bash
# Create account via curl or Postman
POST http://localhost:8001/api/v1/accounts/savings
{
  "name": "Test User",
  "pin": "1357",
  "date_of_birth": "1990-05-15",
  "gender": "Male",
  "phone_no": "9876543210",
  "aadhar_number": "123456789012",
  "privilege": "SILVER",
  "initial_balance": 5000
}

# Then show the logs
cat logs/compliance/created_accounts.txt
```

### Demo 3: Explain Encryption

**Interactive Exercise:**
```python
# In Python console
from app.utils.encryption import EncryptionManager

enc = EncryptionManager()

# Encrypt
secret = "123456789012"
encrypted = enc.encrypt_data(secret)
print(f"Original: {secret}")
print(f"Encrypted: {encrypted}")

# Decrypt
decrypted = enc.decrypt_data(encrypted)
print(f"Decrypted: {decrypted}")
```

**Show trainees:**
- Same input always gives different encrypted output (due to random IV)
- Encrypted text is much longer
- Decryption requires the same key
- Without key, data is unreadable

### Demo 4: CSV Analysis in Excel

**Steps:**
1. Open `audit_log.csv` in Excel
2. Show how to:
   - Sort by timestamp
   - Filter by account number
   - Count total accounts created
   - Create a pivot table

**Excel Formulas to Demonstrate:**
```excel
# Count accounts created today
=COUNTIF(A:A, TODAY())

# Sum of all accounts
=COUNTA(B:B) - 1  # Subtract header row

# Find specific account
=FILTER(A:E, B:B=1001)
```

---

## Teaching Tips

### 1. Use Analogies
- **Logging = Security Camera Footage**: You hope you never need it, but when something goes wrong, it's invaluable
- **Encryption = Safe Deposit Box**: Data is locked away, only accessible with the key
- **CSV vs Text = Digital vs Paper**: Both have their uses

### 2. Show Real Examples
- Bring up actual log files during training
- Show how logs helped debug a real issue
- Demonstrate log analysis for finding patterns

### 3. Common Mistakes to Highlight
```python
# ❌ WRONG: Writing sensitive data in plain text
logger.info(f"PIN: {pin}")  # Never do this!

# ✅ CORRECT: Mask or omit sensitive data
logger.info(f"PIN: ****")  # Safe for logs

# ❌ WRONG: Not handling file errors
with open("log.txt", "a") as f:
    f.write(data)  # What if disk is full?

# ✅ CORRECT: Handle errors gracefully
try:
    with open("log.txt", "a") as f:
        f.write(data)
except IOError as e:
    logger.error(f"Failed to write log: {e}")
    # Alert operations team
```

### 4. Interactive Questions
- "What would happen if we logged PINs in plain text?"
- "How would you find all accounts created last month?"
- "What if a customer disputes a transaction from 6 months ago?"
- "How do we prove to RBI that we're compliant?"

---

## Code Review Checklist for Trainees

When reviewing logging code, check:

- [ ] **No sensitive data in plain text logs**
  - No PINs, passwords, Aadhar numbers
  - Use masking or encryption

- [ ] **Proper log levels used**
  - INFO for normal operations
  - ERROR for failures
  - WARNING for unusual situations

- [ ] **Timestamps included**
  - Every log entry has a timestamp
  - Use consistent format (ISO 8601)

- [ ] **Error handling**
  - Logging failures don't crash the app
  - Errors are logged themselves

- [ ] **File permissions**
  - Log files are not world-readable
  - Only authorized users can access

- [ ] **Log rotation considered**
  - Logs don't grow infinitely
  - Old logs are archived

---

## Advanced Topics (For Interested Trainees)

### 1. Structured Logging (JSON)
```python
import json
import logging

# Instead of plain text
logger.info("Account 1001 created")

# Use structured JSON
logger.info(json.dumps({
    "event": "account_created",
    "account_number": 1001,
    "timestamp": "2026-01-22T09:30:00Z",
    "user_id": "john.doe"
}))
```

**Benefits:**
- Easy to parse programmatically
- Can be ingested by log aggregation tools (ELK stack, Splunk)
- Better for analytics

### 2. Centralized Logging
In production, logs from all microservices go to a central system:
```
accounts_service → 
transactions_service →  [Log Aggregator] → [Dashboard]
users_service → 
auth_service → 
```

**Tools:** ELK Stack (Elasticsearch, Logstash, Kibana), Splunk, Datadog

### 3. Log Levels in Production
```python
# Development
logging.basicConfig(level=logging.DEBUG)  # See everything

# Production
logging.basicConfig(level=logging.INFO)   # Only important stuff

# Critical Production
logging.basicConfig(level=logging.WARNING)  # Only problems
```

---

## Summary for Trainees

### Key Takeaways:
1. **Logging is mandatory** in banking for compliance and debugging
2. **Dual logging** (text + CSV) serves different purposes
3. **Encrypt sensitive data** in logs (Aadhar, PIN)
4. **Mask data** in API responses
5. **Handle logging errors** gracefully
6. **Never log** PINs, passwords in plain text
7. **Retain logs** for 7 years (RBI requirement)

### Best Practices:
- Log at appropriate levels (INFO, ERROR, WARNING)
- Include timestamps in all logs
- Use structured formats (CSV, JSON) for machine processing
- Implement log rotation for large files
- Secure log files with proper permissions
- Test logging in error scenarios

---

## Quick Reference Card

```python
# ✅ Good Logging Practices
logger.info(f"✅ Account {account_number} created")
logger.error(f"❌ Failed to create account: {error_message}")
logger.warning(f"⚠️ Retry attempt {retry_count}/3")

# ❌ Bad Logging Practices
logger.info(f"PIN: {pin}")  # Never log sensitive data!
print("Account created")    # Use logger, not print
logger.debug("x=5")         # Too verbose for production

# File Handling
with open("log.txt", "a") as f:  # "a" = append
    f.write(f"{timestamp}: {message}\n")

# CSV Writing
import csv
with open("audit.csv", "a", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([timestamp, account_number, action])

# Encryption
from app.utils.encryption import EncryptionManager
enc = EncryptionManager()
encrypted = enc.encrypt_data(sensitive_data)
```

---

**Prepared by:** GDB Architecture Team  
**Last Updated:** 2026-01-22  
**For:** Banking Application Training Program  
**Trainees:** 46 Junior Developers
