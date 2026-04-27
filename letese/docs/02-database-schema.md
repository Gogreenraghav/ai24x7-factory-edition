# Letese — Database Schema

## Overview
- **Database:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic
- **Multi-tenant:** Yes (user_id foreign key on all user data)

---

## Tables

### 1. users
Primary user account table.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | Unique identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Login email |
| phone | VARCHAR(20) | UNIQUE, NULL | Phone number |
| password_hash | VARCHAR(255) | NULL | Hashed password (if email/password auth) |
| full_name | VARCHAR(255) | NOT NULL | Display name |
| role | ENUM | NOT NULL, DEFAULT 'user' | user, admin, ca, cs, lawyer |
| is_verified | BOOLEAN | DEFAULT FALSE | Email/phone verified |
| avatar_url | VARCHAR(500) | NULL | Profile picture |
| created_at | TIMESTAMP | DEFAULT NOW() | Account created |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update |
| is_active | BOOLEAN | DEFAULT TRUE | Soft delete flag |

**Indexes:** email (UNIQUE), phone (UNIQUE), role

---

### 2. user_otp
OTP storage for authentication.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK → users.id, NULL | Link to user (null = unverified signup) |
| email | VARCHAR(255) | NOT NULL | OTP sent to this email |
| phone | VARCHAR(20) | NULL | OTP sent to this phone |
| otp_code | VARCHAR(10) | NOT NULL | Hashed OTP |
| otp_type | ENUM | NOT NULL | login, signup, password_reset, phone_verify |
| expires_at | TIMESTAMP | NOT NULL | OTP expiry time |
| used_at | TIMESTAMP | NULL | When OTP was used |
| attempts | INTEGER | DEFAULT 0 | Failed attempts (max 3) |
| created_at | TIMESTAMP | DEFAULT NOW() | OTP generated |

**Indexes:** email + otp_type (composite), expires_at

---

### 3. services
All available legal/compliance services offered.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | Unique identifier |
| slug | VARCHAR(100) | UNIQUE, NOT NULL | URL-friendly name |
| name | VARCHAR(255) | NOT NULL | Service display name |
| name_hi | VARCHAR(255) | NULL | Hindi name |
| description | TEXT | NULL | Short description |
| description_hi | TEXT | NULL | Hindi description |
| category | ENUM | NOT NULL | company_registration, fire_noc, ca_services, cs_services, legal_advisory |
| base_price | DECIMAL(10,2) | NULL | Starting price in INR |
| is_active | BOOLEAN | DEFAULT TRUE | Available for booking |
| icon | VARCHAR(50) | NULL | Icon name/code |
| estimated_days | INTEGER | NULL | Avg. completion days |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** category, slug (UNIQUE), is_active

---

### 4. service_subtypes
Sub-types/variants under a main service.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | Unique identifier |
| service_id | UUID | FK → services.id, NOT NULL | Parent service |
| name | VARCHAR(255) | NOT NULL | Subtype name (e.g., "Private Ltd") |
| name_hi | VARCHAR(255) | NULL | Hindi name |
| description | TEXT | NULL | Details |
| price | DECIMAL(10,2) | NOT NULL | Price for this subtype |
| documents_required | JSONB | DEFAULT '[]' | List of required documents |
| form_fields | JSONB | DEFAULT '[]' | Dynamic form fields config |
| is_active | BOOLEAN | DEFAULT TRUE | |
| created_at | TIMESTAMP | DEFAULT NOW() | |

---

### 5. cases (Service Requests)
The core case/request tracking table.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | Unique identifier |
| case_number | VARCHAR(50) | UNIQUE, NOT NULL | Human-readable ID (LET-2026-00001) |
| user_id | UUID | FK → users.id, NOT NULL | Client who raised the request |
| service_id | UUID | FK → services.id, NOT NULL | Main service |
| subtype_id | UUID | FK → service_subtypes.id, NULL | Subtype selected |
| assigned_to | UUID | FK → users.id, NULL | Assigned professional (CA/CS/Lawyer) |
| status | ENUM | NOT NULL, DEFAULT 'draft' | draft, submitted, under_review, documents_pending, in_progress, pending_payment, completed, cancelled |
| priority | ENUM | DEFAULT 'normal' | low, normal, high, urgent |
| state | VARCHAR(100) | NULL | Indian state for compliance |
| city | VARCHAR(100) | NULL | City |
| pincode | VARCHAR(10) | NULL | |
| business_name | VARCHAR(255) | NULL | For company registration |
| case_data | JSONB | DEFAULT '{}' | Dynamic form responses |
| notes | TEXT | NULL | Internal notes |
| admin_notes | TEXT | NULL | Admin-visible notes |
| submitted_at | TIMESTAMP | NULL | When user submitted |
| completed_at | TIMESTAMP | NULL | When marked completed |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** user_id, assigned_to, status, case_number (UNIQUE), created_at

---

### 6. case_documents
Documents uploaded for a case.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | Unique identifier |
| case_id | UUID | FK → cases.id, NOT NULL | Parent case |
| uploaded_by | UUID | FK → users.id, NOT NULL | Who uploaded |
| document_type | VARCHAR(100) | NOT NULL | e.g., "aadhar_card", "pan_card", "address_proof" |
| file_name | VARCHAR(255) | NOT NULL | Original filename |
| file_url | VARCHAR(500) | NOT NULL | S3/R2 URL |
| file_size | INTEGER | NULL | Size in bytes |
| mime_type | VARCHAR(100) | NULL | MIME type |
| s3_key | VARCHAR(500) | NOT NULL | Storage key |
| status | ENUM | DEFAULT 'uploaded' | uploaded, verified, rejected |
| verified_by | UUID | FK → users.id, NULL | Who verified |
| verified_at | TIMESTAMP | NULL | When verified |
| rejection_reason | TEXT | NULL | Why rejected |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** case_id, uploaded_by, document_type

---

### 7. case_status_history
Audit trail for case status changes.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | Unique identifier |
| case_id | UUID | FK → cases.id, NOT NULL | Parent case |
| changed_by | UUID | FK → users.id, NOT NULL | Who made the change |
| from_status | VARCHAR(50) | NULL | Previous status |
| to_status | VARCHAR(50) | NOT NULL | New status |
| comment | TEXT | NULL | Reason for change |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** case_id, created_at

---

### 8. case_messages
Communication thread on a case.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | Unique identifier |
| case_id | UUID | FK → cases.id, NOT NULL | Parent case |
| sender_id | UUID | FK → users.id, NOT NULL | Who sent |
| message | TEXT | NOT NULL | Message content |
| is_internal | BOOLEAN | DEFAULT FALSE | Only visible to staff (not user) |
| attachments | JSONB | DEFAULT '[]' | [{file_url, file_name}] |
| read_at | TIMESTAMP | NULL | When read by recipient |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** case_id, sender_id, created_at

---

### 9. payments
Payment records for cases.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | Unique identifier |
| case_id | UUID | FK → cases.id, NOT NULL | Associated case |
| user_id | UUID | FK → users.id, NOT NULL | Payer |
| order_id | VARCHAR(100) | UNIQUE, NOT NULL | External payment gateway order ID |
| amount | DECIMAL(10,2) | NOT NULL | Amount in INR |
| currency | VARCHAR(10) | DEFAULT 'INR' | |
| payment_method | VARCHAR(50) | NULL | card, upi, netbanking, wallet |
| status | ENUM | DEFAULT 'pending' | pending, success, failed, refunded |
| gateway | VARCHAR(50) | NULL | razorpay, paystack, stripe |
| gateway_transaction_id | VARCHAR(255) | NULL | |
| payment_data | JSONB | DEFAULT '{}' | Raw gateway response |
| paid_at | TIMESTAMP | NULL | Successful payment time |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** case_id, user_id, order_id (UNIQUE), status

---

### 10. notifications
In-app and push notifications.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK → users.id, NOT NULL | Recipient |
| type | VARCHAR(50) | NOT NULL | case_update, payment_success, document_verify, reminder, system |
| title | VARCHAR(255) | NOT NULL | Notification title |
| message | TEXT | NOT NULL | Body |
| data | JSONB | DEFAULT '{}' | Extra payload (case_id, etc.) |
| is_read | BOOLEAN | DEFAULT FALSE | |
| read_at | TIMESTAMP | NULL | |
| channel | VARCHAR(20) | DEFAULT 'in_app' | in_app, email, sms, push |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** user_id + is_read (composite), created_at

---

### 11. refresh_tokens
JWT refresh token storage.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK → users.id, NOT NULL | Owner |
| token_hash | VARCHAR(255) | NOT NULL | Hashed token |
| device_info | VARCHAR(255) | NULL | Device/browser info |
| ip_address | VARCHAR(50) | NULL | Last known IP |
| expires_at | TIMESTAMP | NOT NULL | Token expiry |
| revoked_at | TIMESTAMP | NULL | When invalidated |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** token_hash, user_id

---

### 12. audit_logs
Admin/system action audit trail.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | Unique identifier |
| actor_id | UUID | FK → users.id, NULL | Who performed action |
| action | VARCHAR(100) | NOT NULL | e.g., "case_status_changed" |
| entity_type | VARCHAR(50) | NOT NULL | e.g., "case", "user", "payment" |
| entity_id | UUID | NULL | ID of affected entity |
| old_value | JSONB | NULL | Previous state |
| new_value | JSONB | NULL | New state |
| ip_address | VARCHAR(50) | NULL | |
| user_agent | VARCHAR(500) | NULL | |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** actor_id, entity_type + entity_id, created_at

---

## Relationships Summary

```
users
 ├── otp (1:many)
 ├── cases (1:many)
 ├── case_documents (1:many)
 ├── case_messages (1:many)
 ├── payments (1:many)
 ├── notifications (1:many)
 ├── refresh_tokens (1:many)
 └── audit_logs (1:many)

services
 └── service_subtypes (1:many)

service_subtypes
 └── cases (1:many)

cases
 ├── case_documents (1:many)
 ├── case_status_history (1:many)
 ├── case_messages (1:many)
 └── payments (1:many)
```

## Key Enums

```sql
-- user role
CREATE TYPE user_role AS ENUM ('user', 'admin', 'ca', 'cs', 'lawyer', 'super_admin');

-- case status
CREATE TYPE case_status AS ENUM (
  'draft', 'submitted', 'under_review', 'documents_pending',
  'in_progress', 'pending_payment', 'completed', 'cancelled', 'rejected'
);

-- payment status
CREATE TYPE payment_status AS ENUM ('pending', 'success', 'failed', 'refunded');

-- document status
CREATE TYPE document_status AS ENUM ('uploaded', 'verified', 'rejected');
```

## Migration Notes
- All UUIDs generated server-side (UUID v4)
- Soft deletes via `is_active` flag (no hard deletes on users/cases)
- All timestamps in UTC
- Money stored as DECIMAL(10,2) — never use FLOAT
- JSONB for flexible/dynamic fields
