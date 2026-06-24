# 🏦 GDB Banking - Account Creation Architecture

> **Complete UML Documentation for Account Creation System**  
> Author: GDB Architecture Team  
> Last Updated: 2025-12-30

---

## 📑 Table of Contents

1. [Overview](#overview)
2. [Class Diagram](#class-diagram)
3. [Sequence Diagram](#sequence-diagram)
4. [Activity Diagram](#activity-diagram)
5. [Component Diagram](#component-diagram)
6. [Design Patterns](#design-patterns)
7. [API Flow Examples](#api-flow-examples)

---

## 🎯 Overview

The GDB Banking Account Creation system uses a **Factory Pattern** with **Interface-based polymorphism** to handle different account types (Savings, Current) through a unified, extensible architecture.

### Key Benefits

✅ **Extensibility**: Add new account types (Fixed Deposit, Recurring Deposit) without modifying existing code  
✅ **Maintainability**: Type-specific logic is encapsulated in separate implementations  
✅ **Testability**: Each component can be tested independently  
✅ **SOLID Principles**: Follows Open/Closed, Single Responsibility, and Dependency Inversion principles

---

## 📊 Class Diagram - Factory Pattern Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          <<interface>>                                  │
│                         AccountImpl                                     │
├─────────────────────────────────────────────────────────────────────────┤
│ + open(account_data, pin_hash): int                                     │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               │ implements
                ┌──────────────┴──────────────┐
                │                             │
┌───────────────▼──────────────┐  ┌──────────▼────────────────┐
│      SavingsImpl             │  │     CurrentImpl           │
├──────────────────────────────┤  ├───────────────────────────┤
│ - repo: AccountRepository    │  │ - repo: AccountRepository │
├──────────────────────────────┤  ├───────────────────────────┤
│ + __init__()                 │  │ + __init__()              │
│ + open(account_data,         │  │ + open(account_data,      │
│        pin_hash): int        │  │        pin_hash): int     │
│   - validate_age(18)         │  │   - validate_company()    │
│   - validate_phone()         │  │   - validate_reg_no()     │
└──────────────────────────────┘  └───────────────────────────┘
                ▲                             ▲
                │                             │
                │ creates                     │ creates
                │                             │
        ┌───────┴─────────────────────────────┴────────┐
        │          AccountFactory                      │
        ├──────────────────────────────────────────────┤
        │ + create(account_type: str): AccountImpl     │
        │   - if 'SAVINGS': return SavingsImpl()       │
        │   - if 'CURRENT': return CurrentImpl()       │
        │   - else: raise ValidationError              │
        └──────────────────┬───────────────────────────┘
                           │
                           │ uses
                           │
        ┌──────────────────▼───────────────────────────┐
        │          AccountService                      │
        ├──────────────────────────────────────────────┤
        │ - repo: AccountRepository                    │
        │ - encryption: EncryptionManager              │
        │ - factory: AccountFactory                    │
        ├──────────────────────────────────────────────┤
        │ + create_savings_account(account): int       │
        │ + create_current_account(account): int       │
        │ - _open_account(type, data): int             │
        │ + get_account_details(acc_no): Account       │
        │ + debit_account(acc_no, amount): bool        │
        │ + credit_account(acc_no, amount): bool       │
        └──────────────────┬───────────────────────────┘
                           │
                           │ uses
                           │
        ┌──────────────────▼───────────────────────────┐
        │        AccountRepository                     │
        ├──────────────────────────────────────────────┤
        │ - db: Database                               │
        ├──────────────────────────────────────────────┤
        │ + create_savings_account(data, pin): int     │
        │ + create_current_account(data, pin): int     │
        │ + get_account(account_number): Account       │
        │ + debit_account(acc_no, amount): bool        │
        │ + credit_account(acc_no, amount): bool       │
        │ + get_pin_hash(account_number): str          │
        └──────────────────────────────────────────────┘
```

### Class Responsibilities

| Class | Responsibility | Pattern Role |
|-------|---------------|--------------|
| `AccountImpl` | Abstract interface for account operations | Interface |
| `SavingsImpl` | Savings-specific validation & creation | Concrete Product |
| `CurrentImpl` | Current account-specific validation & creation | Concrete Product |
| `AccountFactory` | Creates appropriate account implementation | Factory |
| `AccountService` | High-level business logic orchestration | Facade |
| `AccountRepository` | Database operations abstraction | Repository |

---

## 🔄 Sequence Diagram - Savings Account Creation

```
Client    API         Account      Account     Account    Savings    Account      Database
          Endpoint    Service      Factory     Impl       Impl       Repository
  │          │           │            │           │          │            │           │
  │ POST     │           │            │           │          │            │           │
  │─────────>│           │            │           │          │            │           │
  │ /savings │           │            │           │          │            │           │
  │          │           │            │           │          │            │           │
  │          │ Validate  │            │           │          │            │           │
  │          │ JWT Token │            │           │          │            │           │
  │          │ (ADMIN/   │            │           │          │            │           │
  │          │  TELLER)  │            │           │          │            │           │
  │          │           │            │           │          │            │           │
  │          │ create_   │            │           │          │            │           │
  │          │ savings_  │            │           │          │            │           │
  │          │ account() │            │           │          │            │           │
  │          │──────────>│            │           │          │            │           │
  │          │           │            │           │          │            │           │
  │          │           │ _open_     │           │          │            │           │
  │          │           │ account(   │           │          │            │           │
  │          │           │ 'SAVINGS') │           │          │            │           │
  │          │           │───────────>│           │          │            │           │
  │          │           │            │           │          │            │           │
  │          │           │            │ hash_pin()│          │            │           │
  │          │           │            │──────────>│          │            │           │
  │          │           │            │<──────────│          │            │           │
  │          │           │            │ pin_hash  │          │            │           │
  │          │           │            │           │          │            │           │
  │          │           │            │ create(   │          │            │           │
  │          │           │            │ 'SAVINGS')│          │            │           │
  │          │           │            │──────────────────────>│            │           │
  │          │           │            │           │          │            │           │
  │          │           │            │           │ new SavingsImpl()     │           │
  │          │           │            │<──────────────────────│            │           │
  │          │           │            │           │          │            │           │
  │          │           │            │ impl.open(data, hash)│            │           │
  │          │           │            │──────────────────────────────────>│           │
  │          │           │            │           │          │            │           │
  │          │           │            │           │          │ validate_  │           │
  │          │           │            │           │          │ name()     │           │
  │          │           │            │           │          │            │           │
  │          │           │            │           │          │ validate_  │           │
  │          │           │            │           │          │ age(18)    │           │
  │          │           │            │           │          │            │           │
  │          │           │            │           │          │ validate_  │           │
  │          │           │            │           │          │ pin()      │           │
  │          │           │            │           │          │            │           │
  │          │           │            │           │          │ validate_  │           │
  │          │           │            │           │          │ phone()    │           │
  │          │           │            │           │          │            │           │
  │          │           │            │           │          │ repo.create│           │
  │          │           │            │           │          │ _savings() │           │
  │          │           │            │           │          │───────────>│           │
  │          │           │            │           │          │            │           │
  │          │           │            │           │          │            │ BEGIN     │
  │          │           │            │           │          │            │ TRANSACTION│
  │          │           │            │           │          │            │──────────>│
  │          │           │            │           │          │            │           │
  │          │           │            │           │          │            │ nextval(  │
  │          │           │            │           │          │            │ 'seq')    │
  │          │           │            │           │          │            │──────────>│
  │          │           │            │           │          │            │<──────────│
  │          │           │            │           │          │            │ 1001      │
  │          │           │            │           │          │            │           │
  │          │           │            │           │          │            │ INSERT    │
  │          │           │            │           │          │            │ accounts  │
  │          │           │            │           │          │            │──────────>│
  │          │           │            │           │          │            │           │
  │          │           │            │           │          │            │ INSERT    │
  │          │           │            │           │          │            │ savings_  │
  │          │           │            │           │          │            │ details   │
  │          │           │            │           │          │            │──────────>│
  │          │           │            │           │          │            │           │
  │          │           │            │           │          │            │ COMMIT    │
  │          │           │            │           │          │            │──────────>│
  │          │           │            │           │          │            │<──────────│
  │          │           │            │           │          │            │ Success   │
  │          │           │            │           │          │<───────────│           │
  │          │           │            │           │          │ 1001       │           │
  │          │           │            │<──────────────────────────────────│           │
  │          │           │<───────────│           │          │            │           │
  │          │<──────────│            │           │          │            │           │
  │<─────────│            │           │          │            │           │
  │ 201      │            │           │          │            │           │
  │ Created  │            │           │          │            │           │
  │ {acc:1001}           │           │          │            │           │
```

### Sequence Flow Steps

1. **Authentication**: JWT token validated for ADMIN/TELLER role
2. **Service Call**: `AccountService.create_savings_account()` invoked
3. **PIN Hashing**: PIN encrypted using bcrypt
4. **Factory Creation**: Factory returns `SavingsImpl` instance
5. **Validation**: Age, phone, PIN, name validated
6. **Database Transaction**: Account created in 2 tables atomically
7. **Response**: Account number returned to client

---

## 🎯 Activity Diagram - Account Creation Flow

```
                    START
                      │
                      ▼
        ┌─────────────────────────┐
        │ Client sends POST       │
        │ /accounts/savings       │
        └────────────┬────────────┘
                     ▼
        ┌─────────────────────────┐
        │ JWT Authentication      │
        │ Check: ADMIN or TELLER? │
        └────────┬────────────────┘
                 │
          ┌──────┴──────┐
          │             │
      [YES]           [NO]
          │             │
          ▼             ▼
    ┌─────────┐   ┌─────────────┐
    │Continue │   │Return 403   │
    └────┬────┘   │Forbidden    │
         │        └─────────────┘
         │              │
         │              ▼
         │            END
         │
         ▼
┌──────────────────────┐
│ AccountService       │
│ create_savings_      │
│ account()            │
└─────────┬────────────┘
          ▼
┌──────────────────────┐
│ Hash PIN             │
│ pin_hash = hash(pin) │
└─────────┬────────────┘
          ▼
┌──────────────────────┐
│ AccountFactory       │
│ create('SAVINGS')    │
└─────────┬────────────┘
          ▼
┌──────────────────────┐
│ Returns SavingsImpl  │
└─────────┬────────────┘
          ▼
┌──────────────────────┐
│ SavingsImpl.open()   │
│                      │
│ Validations:         │
└─────────┬────────────┘
          │
          ▼
    ┌─────────────┐
    │validate_name│
    └──────┬──────┘
           │
      ┌────┴────┐
      │         │
   [PASS]     [FAIL]
      │         │
      │         ▼
      │    ┌─────────────┐
      │    │Raise        │
      │    │ValidationErr│
      │    └─────────────┘
      │         │
      ▼         ▼
┌──────────┐  END
│validate_ │
│age(18)   │
└────┬─────┘
     │
┌────┴────┐
│         │
[PASS]  [FAIL]
│         │
│         ▼
│    ┌──────────────┐
│    │Raise AgeErr  │
│    └──────────────┘
│         │
▼         ▼
┌──────────┐  END
│validate_ │
│pin()     │
└────┬─────┘
     │
┌────┴────┐
│         │
[PASS]  [FAIL]
│         │
│         ▼
│    ┌──────────────┐
│    │Raise PINErr  │
│    └──────────────┘
│         │
▼         ▼
┌──────────┐  END
│validate_ │
│phone()   │
└────┬─────┘
     │
┌────┴────┐
│         │
[PASS]  [FAIL]
│         │
│         ▼
│    ┌──────────────┐
│    │Raise PhoneErr│
│    └──────────────┘
│         │
▼         ▼
┌──────────────────┐ END
│ All validations  │
│ passed           │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Repository       │
│ create_savings() │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ BEGIN TRANSACTION│
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Generate account │
│ number from seq  │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ INSERT INTO      │
│ accounts table   │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
[SUCCESS]  [FAIL]
    │         │
    │         ▼
    │    ┌─────────────┐
    │    │ROLLBACK     │
    │    │Raise DBError│
    │    └─────────────┘
    │         │
    ▼         ▼
┌──────────┐ END
│ INSERT   │
│ savings_ │
│ details  │
└────┬─────┘
     │
┌────┴────┐
│         │
[SUCCESS] [FAIL]
│         │
│         ▼
│    ┌─────────────┐
│    │ROLLBACK     │
│    │Raise DBError│
│    └─────────────┘
│         │
▼         ▼
┌──────────┐ END
│ COMMIT   │
└────┬─────┘
     ▼
┌──────────────────┐
│ Return account   │
│ number: 1001     │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ API returns 201  │
│ Created          │
└────────┬─────────┘
         ▼
       END
```

### Decision Points

| Decision | Condition | Success Path | Failure Path |
|----------|-----------|--------------|--------------|
| Authentication | JWT valid & role = ADMIN/TELLER | Continue | 403 Forbidden |
| Name Validation | Length 1-255, non-empty | Continue | ValidationError |
| Age Validation | Age ≥ 18 years | Continue | AgeRestrictionError |
| PIN Validation | 4-6 digits, no patterns | Continue | InvalidPINError |
| Phone Validation | 10 digits, Indian format | Continue | ValidationError |
| DB Insert | No constraint violations | Commit | Rollback |

---

## 🏗️ Component Diagram - System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                          │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Frontend   │  │   Postman    │  │  Mobile App  │        │
│  │   (React)    │  │   (Testing)  │  │   (Future)   │        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                  │                  │                │
│         └──────────────────┼──────────────────┘                │
│                            │                                   │
└────────────────────────────┼───────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                      API LAYER                                 │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐     │
│  │  accounts.py (FastAPI Router)                        │     │
│  │  ┌────────────────┐  ┌────────────────┐             │     │
│  │  │ POST /savings  │  │ POST /current  │             │     │
│  │  │ GET /{acc_no}  │  │ PUT /{acc_no}  │             │     │
│  │  │ POST /debit    │  │ POST /credit   │             │     │
│  │  └────────────────┘  └────────────────┘             │     │
│  └──────────────────────────────────────────────────────┘     │
│         │                                                      │
│         │ Depends(require_admin_or_teller)                    │
│         ▼                                                      │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  JWT Authentication & Authorization                  │     │
│  │  (auth_dependencies.py)                              │     │
│  └──────────────────────────────────────────────────────┘     │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                         │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐     │
│  │         AccountService (Facade)                      │     │
│  │  ┌────────────────────────────────────────────┐     │     │
│  │  │ + create_savings_account()                 │     │     │
│  │  │ + create_current_account()                 │     │     │
│  │  │ - _open_account() [Factory Pattern]        │     │     │
│  │  │ + get_account_details()                    │     │     │
│  │  │ + debit_account()                          │     │     │
│  │  │ + credit_account()                         │     │     │
│  │  └────────────────────────────────────────────┘     │     │
│  └─────────────────┬────────────────────────────────────┘     │
│                    │                                           │
│         ┌──────────┼──────────┐                               │
│         │          │          │                               │
│         ▼          ▼          ▼                               │
│  ┌──────────┐ ┌─────────┐ ┌──────────┐                       │
│  │ Account  │ │Encryption│ │Validators│                       │
│  │ Factory  │ │ Manager  │ │ (Utils)  │                       │
│  └────┬─────┘ └──────────┘ └──────────┘                       │
│       │                                                        │
│       │ creates                                                │
│       ▼                                                        │
│  ┌─────────────────────────────────┐                          │
│  │   <<interface>>                 │                          │
│  │   AccountImpl                   │                          │
│  └────────┬────────────────────────┘                          │
│           │                                                    │
│    ┌──────┴──────┐                                            │
│    │             │                                            │
│    ▼             ▼                                            │
│  ┌──────────┐ ┌──────────┐                                   │
│  │ Savings  │ │ Current  │                                   │
│  │   Impl   │ │   Impl   │                                   │
│  └────┬─────┘ └────┬─────┘                                   │
│       │            │                                          │
└───────┼────────────┼───────────────────────────────────────────┘
        │            │
        └──────┬─────┘
               │
               ▼
┌────────────────────────────────────────────────────────────────┐
│                   DATA ACCESS LAYER                            │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐     │
│  │         AccountRepository                            │     │
│  │  ┌────────────────────────────────────────────┐     │     │
│  │  │ + create_savings_account()                 │     │     │
│  │  │ + create_current_account()                 │     │     │
│  │  │ + get_account()                            │     │     │
│  │  │ + get_all_accounts()                       │     │     │
│  │  │ + debit_account()                          │     │     │
│  │  │ + credit_account()                         │     │     │
│  │  │ + get_pin_hash()                           │     │     │
│  │  └────────────────────────────────────────────┘     │     │
│  └─────────────────┬────────────────────────────────────┘     │
│                    │ asyncpg                                   │
└────────────────────┼───────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│                   DATABASE LAYER                               │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐     │
│  │         PostgreSQL Database                          │     │
│  │  ┌────────────────┐  ┌────────────────────────┐     │     │
│  │  │   accounts     │  │ savings_account_details│     │     │
│  │  ├────────────────┤  ├────────────────────────┤     │     │
│  │  │ account_number │  │ account_number (FK)    │     │     │
│  │  │ account_type   │  │ date_of_birth          │     │     │
│  │  │ name           │  │ gender                 │     │     │
│  │  │ pin_hash       │  │ phone_no               │     │     │
│  │  │ balance        │  └────────────────────────┘     │     │
│  │  │ privilege      │                                 │     │
│  │  │ is_active      │  ┌────────────────────────┐     │     │
│  │  │ activated_date │  │ current_account_details│     │     │
│  │  │ closed_date    │  ├────────────────────────┤     │     │
│  │  └────────────────┘  │ account_number (FK)    │     │     │
│  │                      │ company_name           │     │     │
│  │  ┌────────────────┐  │ website                │     │     │
│  │  │ Sequences      │  │ registration_no        │     │     │
│  │  ├────────────────┤  └────────────────────────┘     │     │
│  │  │account_number_ │                                 │     │
│  │  │seq (start:1000)│                                 │     │
│  │  └────────────────┘                                 │     │
│  └──────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Components | Responsibility |
|-------|-----------|----------------|
| **Presentation** | React Frontend, Postman | User interaction, API consumption |
| **API** | FastAPI Router, JWT Auth | Request validation, authorization |
| **Business Logic** | Service, Factory, Impl | Business rules, validation, orchestration |
| **Data Access** | Repository | Database abstraction, CRUD operations |
| **Database** | PostgreSQL | Data persistence, constraints, transactions |

---

## 🎨 Design Patterns Used

### 1. Factory Pattern

```
┌─────────────────────────────────────────────────────────┐
│  PATTERN: FACTORY PATTERN                               │
├─────────────────────────────────────────────────────────┤
│  Purpose: Create account implementations dynamically    │
│                                                          │
│  ┌─────────────┐                                        │
│  │   Client    │                                        │
│  └──────┬──────┘                                        │
│         │ needs account                                 │
│         ▼                                                │
│  ┌─────────────┐                                        │
│  │  Factory    │                                        │
│  └──────┬──────┘                                        │
│         │ creates                                       │
│    ┌────┴────┐                                          │
│    │         │                                          │
│    ▼         ▼                                          │
│ ┌──────┐ ┌──────┐                                       │
│ │Savings│ │Current│                                      │
│ └──────┘ └──────┘                                       │
└─────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ Centralized object creation
- ✅ Easy to add new account types
- ✅ Decouples client from concrete classes

**Implementation:**
```python
# app/services/account_factory.py
class AccountFactory:
    def create(self, account_type: str) -> AccountImpl:
        if account_type == 'SAVINGS':
            return SavingsImpl()
        elif account_type == 'CURRENT':
            return CurrentImpl()
        else:
            raise ValidationError(f"Unsupported account type: {account_type}")
```

---

### 2. Strategy Pattern (via Interface)

```
┌─────────────────────────────────────────────────────────┐
│  PATTERN: STRATEGY PATTERN (via Interface)              │
├─────────────────────────────────────────────────────────┤
│  Purpose: Different validation strategies per type      │
│                                                          │
│  AccountImpl.open() ← Interface                         │
│         │                                                │
│    ┌────┴────┐                                          │
│    │         │                                          │
│    ▼         ▼                                          │
│ SavingsImpl  CurrentImpl                                │
│ - age ≥ 18   - company validation                       │
│ - phone      - registration_no                          │
└─────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ Type-specific validation logic
- ✅ Polymorphic behavior
- ✅ Open/Closed principle compliance

**Implementation:**
```python
# Savings-specific validations
class SavingsImpl(AccountImpl):
    async def open(self, account_data, pin_hash):
        validate_age(account_data.date_of_birth, min_age=18)
        validate_phone_number(account_data.phone_no, country="IN")
        # ...

# Current-specific validations
class CurrentImpl(AccountImpl):
    async def open(self, account_data, pin_hash):
        validate_company_name(account_data.company_name)
        validate_registration_no(account_data.registration_no)
        # ...
```

---

### 3. Facade Pattern

```
┌─────────────────────────────────────────────────────────┐
│  PATTERN: FACADE PATTERN                                │
├─────────────────────────────────────────────────────────┤
│  Purpose: Simplify complex subsystem                    │
│                                                          │
│  ┌─────────────────┐                                    │
│  │ AccountService  │ ← Simple interface                 │
│  │  (Facade)       │                                    │
│  └────────┬────────┘                                    │
│           │ coordinates                                 │
│     ┌─────┼─────┬─────┐                                │
│     ▼     ▼     ▼     ▼                                │
│  Factory Repo Encrypt Valid                             │
└─────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ Simplified API for clients
- ✅ Hides subsystem complexity
- ✅ Loose coupling

**Implementation:**
```python
class AccountService:
    def __init__(self):
        self.repo = AccountRepository()
        self.encryption = EncryptionManager()
        self.factory = AccountFactory()
    
    async def create_savings_account(self, account):
        # Simple public interface
        return await self._open_account('SAVINGS', account)
```

---

### 4. Repository Pattern

```
┌─────────────────────────────────────────────────────────┐
│  PATTERN: REPOSITORY PATTERN                            │
├─────────────────────────────────────────────────────────┤
│  Purpose: Abstract data access                          │
│                                                          │
│  Business Logic                                         │
│         │                                                │
│         ▼                                                │
│  ┌─────────────┐                                        │
│  │ Repository  │ ← Abstract interface                   │
│  └──────┬──────┘                                        │
│         │                                                │
│         ▼                                                │
│    Database                                             │
└─────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ Database abstraction
- ✅ Testability (mock repository)
- ✅ Centralized data access logic

**Implementation:**
```python
class AccountRepository:
    async def create_savings_account(self, account_data, pin_hash):
        async with self.db.transaction() as conn:
            account_number = await conn.fetchval("SELECT nextval('account_number_seq')")
            await conn.execute("INSERT INTO accounts (...)")
            await conn.execute("INSERT INTO savings_account_details (...)")
            return account_number
```

---

## 📝 API Flow Examples

### Example 1: Create Savings Account

**Request:**
```http
POST /accounts/savings HTTP/1.1
Host: localhost:8001
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "Rajesh Kumar",
  "pin": "1234",
  "date_of_birth": "1990-05-15",
  "gender": "Male",
  "phone_no": "9876543210",
  "privilege": "SILVER"
}
```

**Flow:**
```
Client
  ↓ POST /accounts/savings
API Endpoint (accounts.py:76)
  ↓ Validate JWT (ADMIN/TELLER)
  ↓ Parse SavingsAccountCreate model
AccountService.create_savings_account()
  ↓ _open_account('SAVINGS', data)
  ↓ hash_pin("1234") → "$2b$12$..."
AccountFactory.create('SAVINGS')
  ↓ return SavingsImpl()
SavingsImpl.open(data, pin_hash)
  ↓ validate_name("Rajesh Kumar") ✓
  ↓ validate_age("1990-05-15") ✓ (34 years)
  ↓ validate_pin("1234") ✓
  ↓ validate_phone("9876543210") ✓
AccountRepository.create_savings_account()
  ↓ BEGIN TRANSACTION
  ↓ nextval('account_number_seq') → 1001
  ↓ INSERT INTO accounts (1001, 'SAVINGS', 'Rajesh Kumar', ...)
  ↓ INSERT INTO savings_account_details (1001, '1990-05-15', ...)
  ↓ COMMIT
  ↓ return 1001
Response
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "account_number": 1001,
  "account_type": "SAVINGS",
  "name": "Rajesh Kumar",
  "balance": 0.0,
  "privilege": "SILVER",
  "is_active": true,
  "activated_date": "2025-12-30T15:11:09.123456"
}
```

---

### Example 2: Create Current Account

**Request:**
```http
POST /accounts/current HTTP/1.1
Host: localhost:8001
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "Tech Solutions Pvt Ltd",
  "pin": "5678",
  "company_name": "Tech Solutions",
  "website": "https://techsolutions.com",
  "registration_no": "U74999DL2020PTC123456",
  "privilege": "GOLD"
}
```

**Flow:**
```
Client
  ↓ POST /accounts/current
API Endpoint (accounts.py:130)
  ↓ Validate JWT (ADMIN/TELLER)
  ↓ Parse CurrentAccountCreate model
AccountService.create_current_account()
  ↓ _open_account('CURRENT', data)
  ↓ hash_pin("5678") → "$2b$12$..."
AccountFactory.create('CURRENT')
  ↓ return CurrentImpl()
CurrentImpl.open(data, pin_hash)
  ↓ validate_name("Tech Solutions Pvt Ltd") ✓
  ↓ validate_pin("5678") ✓
  ↓ validate_privilege("GOLD") ✓
AccountRepository.create_current_account()
  ↓ BEGIN TRANSACTION
  ↓ nextval('account_number_seq') → 1002
  ↓ INSERT INTO accounts (1002, 'CURRENT', 'Tech Solutions Pvt Ltd', ...)
  ↓ INSERT INTO current_account_details (1002, 'Tech Solutions', ...)
  ↓ COMMIT
  ↓ return 1002
Response
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "account_number": 1002,
  "account_type": "CURRENT",
  "name": "Tech Solutions Pvt Ltd",
  "balance": 0.0,
  "privilege": "GOLD",
  "is_active": true,
  "activated_date": "2025-12-30T15:11:09.456789"
}
```

---

## 🔍 Key Takeaways

### ✅ What Changed (Refactoring)

| Before | After |
|--------|-------|
| ❌ if/else branching in service | ✅ Factory pattern with polymorphism |
| ❌ Monolithic validation logic | ✅ Type-specific implementations |
| ❌ Hard to add new account types | ✅ Just add new Impl class |
| ❌ Tight coupling | ✅ Loose coupling via interfaces |

### ✅ What Stayed the Same (Backward Compatibility)

| Component | Status |
|-----------|--------|
| API Endpoints | ✅ No changes required |
| Request/Response Models | ✅ Unchanged |
| Repository Methods | ✅ Unchanged |
| Database Schema | ✅ Unchanged |
| Client Integration | ✅ Fully compatible |

### ✅ How to Extend (Add Fixed Deposit)

1. **Create Implementation:**
   ```python
   # app/services/fixed_deposit_impl.py
   class FixedDepositImpl(AccountImpl):
       async def open(self, account_data, pin_hash):
           validate_min_deposit(account_data.initial_amount, min=10000)
           validate_tenure(account_data.tenure_months, min=6, max=120)
           # ...
   ```

2. **Update Factory:**
   ```python
   # app/services/account_factory.py
   def create(self, account_type: str):
       if account_type == 'FIXED_DEPOSIT':
           return FixedDepositImpl()
       # ...
   ```

3. **Add Repository Method:**
   ```python
   # app/repositories/account_repo.py
   async def create_fixed_deposit_account(self, account_data, pin_hash):
       # DB logic
   ```

4. **Add API Endpoint:**
   ```python
   # app/api/accounts.py
   @router.post("/accounts/fixed-deposit")
   async def create_fixed_deposit_account(...):
       return await account_service.create_fixed_deposit_account(request)
   ```

**That's it!** No changes to existing code. 🎯

---

## 📚 References

- **Factory Pattern**: [Refactoring Guru - Factory Method](https://refactoring.guru/design-patterns/factory-method)
- **Repository Pattern**: [Martin Fowler - Repository](https://martinfowler.com/eaaCatalog/repository.html)
- **SOLID Principles**: [Uncle Bob - SOLID](https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html)
- **FastAPI Best Practices**: [FastAPI Documentation](https://fastapi.tiangolo.com/tutorial/)

---

## 📞 Contact

For questions or clarifications about this architecture:

- **Team**: GDB Architecture Team
- **Documentation**: See `REFACTORING_FACTORY_PATTERN.md` for implementation details
- **Code Location**: `accounts_service/app/services/`

---

**Last Updated**: 2025-12-30  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
