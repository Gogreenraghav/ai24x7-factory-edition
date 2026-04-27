# Letese — FastAPI Backend Structure

## Overview
Complete file-by-file breakdown of the FastAPI backend. Organized by layers: core config, models, schemas, API routes, services, and utilities.

**Stack:** Python 3.11+ | FastAPI | SQLAlchemy 2.0 (async) | PostgreSQL | Pydantic v2 | Alembic | Redis (caching) | Celery (background tasks)

---

## Project Root Structure

```
letese-backend/
│
├── alembic/                      # Database migrations
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py
│
├── app/
│   ├── __init__.py               # "from app.api.routes import router"
│   ├── main.py                   # FastAPI app entry point
│   │
│   ├── api/                      # Route handlers
│   │   ├── __init__.py
│   │   ├── deps.py               # Shared dependencies (auth, db, current_user)
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py           # /auth/* endpoints
│   │       ├── users.py          # /users/* endpoints
│   │       ├── services.py       # /services/* endpoints
│   │       ├── cases.py          # /cases/* endpoints
│   │       ├── documents.py      # /documents/* endpoints
│   │       ├── messages.py       # /messages/* endpoints
│   │       ├── payments.py        # /payments/* endpoints
│   │       └── notifications.py  # /notifications/* endpoints
│   │
│   ├── core/                     # Core config & security
│   │   ├── __init__.py
│   │   ├── config.py             # Environment variables (pydantic-settings)
│   │   ├── security.py          # JWT creation, password hashing
│   │   ├── database.py          # Async SQLAlchemy engine & session
│   │   ├── redis.py             # Redis connection
│   │   └── email.py             # Email sending (SendGrid/Resend)
│   │
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py              # User, UserOTP, RefreshToken
│   │   ├── service.py          # Service, ServiceSubtype
│   │   ├── case.py             # Case, CaseDocument, CaseStatusHistory, CaseMessage
│   │   ├── payment.py          # Payment
│   │   ├── notification.py     # Notification
│   │   └── audit.py            # AuditLog
│   │
│   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py             # Login, Register, OTP, Token schemas
│   │   ├── user.py             # UserCreate, UserUpdate, UserResponse
│   │   ├── service.py         # Service schemas
│   │   ├── case.py            # CaseCreate, CaseUpdate, CaseResponse
│   │   ├── document.py         # Document schemas
│   │   ├── message.py         # Message schemas
│   │   ├── payment.py         # Payment schemas
│   │   ├── notification.py   # Notification schemas
│   │   └── common.py          # Paginated response, Error response
│   │
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py    # Auth business logic
│   │   ├── user_service.py    # User management logic
│   │   ├── service_service.py # Service catalog logic
│   │   ├── case_service.py    # Case management logic
│   │   ├── document_service.py # Document upload/verify logic
│   │   ├── message_service.py  # Messaging logic
│   │   ├── payment_service.py  # Payment processing logic
│   │   ├── notification_service.py # In-app/email/push notifications
│   │   └── email_service.py    # Email templates & sending
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── storage.py          # S3/R2 file upload utilities
│       ├── otp.py              # OTP generation & validation
│       ├── case_number.py     # Case number generator (LET-YYYY-NNNNN)
│       ├── enums.py            # Enum definitions
│       └── helpers.py          # General helpers
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_cases.py
│   └── test_services/
│
├── scripts/
│   ├── seed_services.py        # Seed initial services data
│   └── create_admin.py          # Create first admin user
│
├── .env.example                 # Environment variable template
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## File-by-File Details

### app/__init__.py
```python
# Imports and re-exports for cleaner imports elsewhere
from app.api.routes import router
```

---

### app/main.py
FastAPI app creation, CORS, middleware, exception handlers, startup events.

**Key components:**
- `FastAPI` app with title="Letese API", version="1.0.0"
- CORS middleware (allow FlutterFlow domain + production domains)
- `TrustedHostMiddleware` for security
- Exception handlers: `HTTPException`, `ValidationError` → JSON error responses
- Startup: connect DB, connect Redis, seed services
- Shutdown: dispose DB engine, close Redis
- Include router: `app.include_router(router, prefix="/api/v1")`
- Health check: `GET /health` → `{"status": "ok", "version": "1.0.0"}`

---

### app/core/config.py
Environment variables using `pydantic-settings`.

```python
# Settings groups:
# Database: DATABASE_URL, SYNC_DATABASE_URL
# Redis: REDIS_URL
# JWT: SECRET_KEY, ALGORITHM ("HS256"), ACCESS_TOKEN_EXPIRE_MINUTES (30), REFRESH_TOKEN_EXPIRE_DAYS (7)
# AWS S3: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET_NAME
# SendGrid: SENDGRID_API_KEY, FROM_EMAIL
# Razorpay: RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
# App: APP_ENV ("development"|"production"), FRONTEND_URL
# OTP: OTP_EXPIRE_MINUTES (5), OTP_MAX_ATTEMPTS (3)
```

---

### app/core/security.py
JWT and password utilities.

```python
# Functions:
# hash_password(password: str) -> str  # bcrypt/scrypt
# verify_password(plain: str, hashed: str) -> bool
# create_access_token(data: dict, expires_delta: timedelta) -> str  # JWT encode
# create_refresh_token(data: dict, expires_delta: timedelta) -> str
# decode_token(token: str) -> dict  # JWT decode, raises if expired/invalid
# generate_otp() -> str  # 6-digit random
# hash_otp(otp: str) -> str  # hash before storing
# verify_otp(plain: str, hashed: str) -> bool
```

---

### app/core/database.py
Async SQLAlchemy setup.

```python
# engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
# async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
# get_db() → async generator yielding session
# Base = declarative_base()
# All models inherit from Base
# init_db() → creates all tables (dev only, use Alembic for prod)
```

---

### app/core/redis.py
```python
# redis_client = aioredis.from_url(REDIS_URL)
# Caching functions: get_cached, set_cached, delete_cached
# OTP rate limiting: incr_otp_attempts(user_id) with TTL
# Session invalidation
```

---

### app/core/email.py
```python
# send_email(to: str, subject: str, template: str, data: dict)
# Templates: welcome.html, otp_verification.html, password_reset.html,
#            case_status_update.html, payment_confirmation.html
# Uses SendGrid API or Resend API
# Async sending (fire-and-forget with Celery)
```

---

## Models (app/models/)

### app/models/user.py
```python
# User: id(UUID), email, phone, password_hash, full_name, role(enum),
#       is_verified, avatar_url, created_at, updated_at, is_active
# UserOTP: id, user_id, email, phone, otp_code(hash), otp_type,
#          expires_at, used_at, attempts, created_at
# RefreshToken: id, user_id, token_hash, device_info, ip_address,
#               expires_at, revoked_at, created_at
```

### app/models/service.py
```python
# Service: id, slug, name, name_hi, description, description_hi,
#          category(enum), base_price, is_active, icon, estimated_days, created_at
# ServiceSubtype: id, service_id, name, name_hi, description, price,
#                 documents_required(JSONB), form_fields(JSONB), is_active, created_at
```

### app/models/case.py
```python
# Case: id, case_number, user_id, service_id, subtype_id, assigned_to,
#       status(enum), priority(enum), state, city, pincode, business_name,
#       case_data(JSONB), notes, admin_notes, submitted_at, completed_at,
#       created_at, updated_at
# CaseDocument: id, case_id, uploaded_by, document_type, file_name,
#                file_url, file_size, mime_type, s3_key, status(enum),
#                verified_by, verified_at, rejection_reason, created_at
# CaseStatusHistory: id, case_id, changed_by, from_status, to_status,
#                    comment, created_at
# CaseMessage: id, case_id, sender_id, message, is_internal,
#              attachments(JSONB), read_at, created_at
```

### app/models/payment.py
```python
# Payment: id, case_id, user_id, order_id, amount, currency,
#          payment_method, status(enum), gateway, gateway_transaction_id,
#          payment_data(JSONB), paid_at, created_at
```

### app/models/notification.py
```python
# Notification: id, user_id, type, title, message, data(JSONB),
#               is_read, read_at, channel, created_at
```

### app/models/audit.py
```python
# AuditLog: id, actor_id, action, entity_type, entity_id,
#           old_value(JSONB), new_value(JSONB), ip_address, user_agent, created_at
```

---

## Schemas (app/schemas/)

### app/schemas/common.py
```python
# PaginatedResponse[T]: items: list[T], total: int, page: int, per_page: int,
#                        total_pages: int, has_next: bool, has_prev: bool
# ErrorResponse: detail: str, code: str | None, errors: list | None
# SuccessResponse: message: str, data: dict | None
```

### app/schemas/auth.py
```python
# UserRegister: email, password, full_name, phone (optional)
# UserLogin: email, password
# OTPVerify: email, otp_code
# ForgotPassword: email
# ResetPassword: email, otp_code, new_password
# TokenResponse: access_token, refresh_token, token_type ("bearer")
# RefreshTokenRequest: refresh_token
```

### app/schemas/user.py
```python
# UserResponse: id, email, phone, full_name, role, is_verified, avatar_url, created_at
# UserUpdate: full_name, phone, avatar_url
# UserProfileResponse: UserResponse + stats (total_cases, completed_cases, etc.)
```

### app/schemas/case.py
```python
# CaseCreate: service_id, subtype_id, state, city, pincode, business_name, case_data
# CaseUpdate: status, priority, notes, admin_notes, assigned_to, case_data
# CaseResponse: all fields + service_name, subtype_name, assigned_to_user, documents_count
# CaseListResponse: PaginatedResponse[CaseResponse]
# CaseStatusUpdate: status, comment (optional)
```

### app/schemas/document.py
```python
# DocumentUploadResponse: id, file_url, file_name, document_type
# DocumentResponse: all document fields + uploaded_by_user
```

### app/schemas/message.py
```python
# MessageCreate: message, attachments (list of {file_url, file_name})
# MessageResponse: id, case_id, sender_id, message, is_internal,
#                  attachments, read_at, created_at, sender (UserResponse)
```

### app/schemas/payment.py
```python
# PaymentInitiate: case_id
# PaymentResponse: id, order_id, amount, currency, status, gateway,
#                   razorpay_order_id, razorpay_payment_url
# PaymentWebhook: razorpay webhook payload
```

### app/schemas/notification.py
```python
# NotificationResponse: id, type, title, message, data, is_read, created_at
```

---

## API Routes (app/api/routes/)

### app/api/deps.py
Shared FastAPI dependencies:
```python
# get_db() → AsyncSession  (from database.py)
# get_redis() → Redis
# get_current_user() → User  (from JWT Bearer token)
# get_current_active_user() → User  (checks is_active)
# get_current_admin_user() → User  (checks role == admin)
# get_current_professional() → User  (checks role in [ca, cs, lawyer])
# PaginationParams: page=1, per_page=20, max_per_page=100
```

### app/api/routes/auth.py
```
POST /auth/register       → Create user, send OTP, return temp token
POST /auth/login          → Verify credentials, create tokens, return tokens
POST /auth/verify-otp     → Verify OTP, mark user verified, return tokens
POST /auth/resend-otp     → Resend OTP (rate limit: 1/min)
POST /auth/forgot-password → Send password reset OTP
POST /auth/reset-password  → Reset password with OTP
POST /auth/refresh-token  → Exchange refresh token for new access token
POST /auth/logout         → Revoke refresh token
GET  /auth/me             → Get current user (protected)
```

### app/api/routes/users.py
```
GET  /users/me           → Current user profile
PUT  /users/me           → Update profile (name, phone)
POST /users/me/avatar    → Upload avatar image
DELETE /users/me/avatar  → Remove avatar
GET  /users/me/stats     → Dashboard stats (case counts, spending)
```

### app/api/routes/services.py
```
GET  /services           → List all active services (with pagination, category filter)
GET  /services/{slug}     → Service detail + subtypes
GET  /services/categories → List all categories
Admin:
POST /services           → Create new service
PUT  /services/{id}       → Update service
DELETE /services/{id}     → Soft-delete service
POST /services/{id}/subtypes → Add subtype
PUT  /services/subtypes/{id} → Update subtype
```

### app/api/routes/cases.py
```
GET  /cases              → List user's cases (paginated, filterable by status)
POST /cases              → Create new case (draft)
GET  /cases/{id}         → Case detail
PUT  /cases/{id}         → Update case (form data)
POST /cases/{id}/submit  → Submit case (draft → submitted)
POST /cases/{id}/cancel → Cancel case
GET  /cases/{id}/timeline → Status history
Admin/Professional:
GET  /admin/cases        → All cases (with filters)
PUT  /cases/{id}/status  → Update status (with history entry)
PUT  /cases/{id}/assign  → Assign to professional
POST /cases/{id}/notes   → Add internal note
```

### app/api/routes/documents.py
```
POST /cases/{case_id}/documents → Upload document (multipart/form-data)
GET  /cases/{case_id}/documents  → List documents for case
GET  /documents/{id}            → Document detail + presigned download URL
DELETE /documents/{id}          → Delete document (owner or admin)
Admin:
PUT  /documents/{id}/verify    → Mark document verified/rejected
```

### app/api/routes/messages.py
```
GET  /cases/{case_id}/messages → List messages (paginated)
POST /cases/{case_id}/messages → Send message (with optional attachments)
PUT  /messages/{id}/read        → Mark message as read
GET  /cases/{case_id}/messages/unread-count → Unread count
```

### app/api/routes/payments.py
```
POST /payments/initiate  → Create Razorpay order
POST /payments/confirm   → Confirm payment (after gateway redirect)
POST /payments/webhook   → Razorpay webhook (HMAC verified)
GET  /payments/{id}      → Payment detail
GET  /payments/history  → User's payment history
```

### app/api/routes/notifications.py
```
GET  /notifications     → List notifications (paginated, unread filter)
PUT  /notifications/{id}/read → Mark as read
PUT  /notifications/read-all  → Mark all read
GET  /notifications/unread-count → Unread count
```

---

## Services (app/services/)

### app/services/auth_service.py
```python
# register_user(data: UserRegister) → User + OTP
# verify_otp(email: str, otp: str) → TokenPair
# login_user(email: str, password: str) → TokenPair
# refresh_access_token(refresh_token: str) → AccessToken
# logout_user(user_id: str, refresh_token: str) → None
# forgot_password(email: str) → OTP sent
# reset_password(email: str, otp: str, new_password: str) → Success
# revoke_all_user_tokens(user_id: str) → None
```

### app/services/case_service.py
```python
# create_case(user_id, data: CaseCreate) → Case
# submit_case(case_id, user_id) → Case  # moves draft → submitted
# update_case(case_id, user_id, data) → Case
# cancel_case(case_id, user_id) → Case
# get_case(case_id, user_id) → CaseResponse  (with relations)
# list_cases(user_id, filters) → PaginatedResponse
# generate_case_number() → str  # "LET-2026-00001"
# update_case_status_admin(case_id, new_status, actor_id, comment) → Case
# assign_case(case_id, professional_id, actor_id) → Case
# add_case_note(case_id, note, actor_id) → CaseNote
```

### app/services/document_service.py
```python
# upload_document(case_id, uploaded_by, file, document_type) → CaseDocument
# generate_presigned_url(s3_key: str, operation: str = "get") → str
# delete_document(document_id, user_id) → None
# verify_document(document_id, verifier_id, status) → CaseDocument
```

### app/services/payment_service.py
```python
# initiate_payment(case_id, user_id) → PaymentOrder (Razorpay order)
# confirm_payment(order_id, payment_data) → Payment
# handle_razorpay_webhook(event: dict) → None
# get_payment(payment_id, user_id) → Payment
# refund_payment(payment_id, admin_id) → Payment
```

### app/services/notification_service.py
```python
# send_notification(user_id, type, title, message, data, channel)
# notify_case_update(case_id, user_id, new_status, message)
# notify_payment_success(case_id, user_id, amount)
# notify_document_status(document_id, status)
# notify_new_message(case_id, recipient_id, sender_name)
# notify_assignment(case_id, professional_id)
# batch_notify_user(user_id, notifications: list)  # for email digest
```

### app/services/email_service.py
```python
# send_welcome_email(user: User) → None (via Celery)
# send_otp_email(email: str, otp: str, otp_type: str) → None
# send_case_status_email(case: Case, user: User) → None
# send_payment_confirmation(payment: Payment, user: User) → None
# send_new_message_email(message: CaseMessage, recipient: User) → None
# send_document_verified_email(document: CaseDocument, user: User) → None
```

---

## Utils (app/utils/)

### app/utils/storage.py
```python
# S3Manager class:
# upload_file(file_obj, folder: str, filename: str, content_type: str) → s3_key
# delete_file(s3_key: str) → None
# generate_presigned_url(s3_key: str, expires_in: int = 3600) → str
# generate_presigned_upload_url(s3_key: str, content_type: str) → str
# copy_file(source_key: str, dest_key: str) → None
# get_public_url(s3_key: str) → str
```

### app/utils/case_number.py
```python
# generate_case_number(db: AsyncSession) → str
# Logic: "LET-{YEAR}-{SEQUENCE:05d}"
# SEQUENCE resets each year, auto-increments from DB
# Uses SELECT FOR UPDATE to prevent race conditions
# Example: LET-2026-00001, LET-2026-00002, ...
```

### app/utils/otp.py
```python
# generate_otp() → str  # 6 random digits
# store_otp(user_id: str, email: str, otp_type: str) → None  # Redis with TTL
# verify_otp_rate_limit(key: str) → bool  # max 3 attempts per 5 min
# get_otp(key: str) → str | None
# invalidate_otp(key: str) → None
```

### app/utils/enums.py
```python
# UserRole = Enum("user_role", ["user", "admin", "ca", "cs", "lawyer", "super_admin"])
# CaseStatus = Enum("case_status", ["draft", "submitted", "under_review",
#           "documents_pending", "in_progress", "pending_payment", "completed",
#           "cancelled", "rejected"])
# PaymentStatus = Enum("payment_status", ["pending", "success", "failed", "refunded"])
# DocumentStatus = Enum("document_status", ["uploaded", "verified", "rejected"])
# NotificationType = Enum("notification_type", ["case_update", "payment_success",
#           "document_verify", "message", "reminder", "system"])
# ServiceCategory = Enum("service_category", ["company_registration", "fire_noc",
#           "ca_services", "cs_services", "legal_advisory"])
```

---

## Background Tasks (Celery)

```
celery/
├── __init__.py
├── celery_app.py        # Celery instance
├── tasks/
│   ├── __init__.py
│   ├── email_tasks.py   # send_email_async, send_bulk_email
│   ├── notification_tasks.py
│   └── cleanup_tasks.py  # Delete expired OTPs, old temp files
```

---

## Alembic Migrations

```
alembic/versions/
├── 001_initial_schema.py       # All tables v1
├── 002_add_case_indexes.py      # Performance indexes
├── 003_add_soft_delete.py       # is_active on users
└── 004_add_compound_indexes.py  # Composite indexes for queries
```

---

## Docker / Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN alembic upgrade head   # Run migrations on startup
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
- `api` service: FastAPI + uvicorn
- `worker` service: Celery worker
- `redis` service: Redis
- `postgres` service: PostgreSQL 15
```

---

## Environment Variables (.env.example)

```env
# App
APP_ENV=development
SECRET_KEY=your-secret-key-here-min-32-chars
FRONTEND_URL=http://localhost:4200

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/letese
SYNC_DATABASE_URL=postgresql://postgres:password@localhost:5432/letese

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AWS S3
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=ap-south-1
S3_BUCKET_NAME=letese-documents

# Email (SendGrid)
SENDGRID_API_KEY=
FROM_EMAIL=noreply@letese.co
FROM_NAME=Letese

# Razorpay
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=

# OTP
OTP_EXPIRE_MINUTES=5
OTP_MAX_ATTEMPTS=3
```
