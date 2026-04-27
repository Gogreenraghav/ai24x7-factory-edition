# LETESE — FastAPI Backend Structure (File-by-File)

## Overview
**Stack:** Python 3.11+ | FastAPI | SQLAlchemy 2.0 (async) | PostgreSQL + pgvector | Redis | Kafka | Celery
**Location:** Server 43.242.224.231
**Port:** 4007 (must replace ZUMMP API)

---

## Project Structure

```
letese-backend/
│
├── alembic/                      # Database migrations
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│       ├── 001_create_tenants.sql
│       ├── 002_add_tenant_id.sql
│       └── 003_create_missing_tables.sql
│
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry
│   │
│   ├── api/
│   │   ├── __init__.py          # router = APIRouter()
│   │   ├── deps.py              # Shared dependencies
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py          # /auth/*
│   │       ├── advocates.py     # /advocates/*
│   │       ├── cases.py         # /cases/*
│   │       ├── clients.py       # /clients/*
│   │       ├── documents.py     # /documents/*
│   │       ├── drafts.py        # /drafts/* (AI drafting)
│   │       ├── court_orders.py  # /court-orders/*
│   │       ├── communications.py # /communications/*
│   │       ├── invoices.py      # /invoices/*
│   │       ├── payments.py      # /payments/*
│   │       ├── subscriptions.py # /subscriptions/*
│   │       ├── reminders.py    # /reminders/*
│   │       ├── translations.py  # /translations/*
│   │       ├── voice_calls.py   # /voice-calls/*
│   │       ├── scraping.py      # /scraping/*
│   │       ├── research.py      # /research/* (pgvector search)
│   │       ├── landing_pages.py # /landing-pages/*
│   │       ├── tasks.py         # /tasks/*
│   │       ├── notifications.py # /notifications/*
│   │       └── admin.py         # /admin/* (Super Admin)
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # pydantic-settings
│   │   ├── security.py         # JWT, password hashing
│   │   ├── database.py         # Async SQLAlchemy engine
│   │   ├── redis_client.py     # Redis connection
│   │   ├── kafka_client.py     # Kafka producer/consumer
│   │   └── tenant.py           # Multi-tenant context
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── tenant.py
│   │   ├── advocate.py
│   │   ├── client.py
│   │   ├── case.py
│   │   ├── document.py
│   │   ├── draft.py
│   │   ├── court_order.py
│   │   ├── ai_suggestion.py
│   │   ├── task.py
│   │   ├── communication.py
│   │   ├── invoice.py
│   │   ├── payment.py
│   │   ├── subscription.py
│   │   ├── landing_page.py
│   │   ├── reminder.py
│   │   ├── translation_job.py
│   │   ├── voice_call_log.py
│   │   ├── api_vendor_config.py
│   │   ├── scraper_job.py
│   │   ├── vector_cache.py
│   │   ├── audit_log.py
│   │   └── deleted_data_archive.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py            # PaginatedResponse, ErrorResponse
│   │   ├── auth.py
│   │   ├── advocate.py
│   │   ├── client.py
│   │   ├── case.py
│   │   ├── document.py
│   │   ├── draft.py
│   │   ├── court_order.py
│   │   ├── task.py
│   │   ├── communication.py
│   │   ├── invoice.py
│   │   ├── payment.py
│   │   ├── subscription.py
│   │   ├── reminder.py
│   │   ├── translation.py
│   │   ├── voice_call.py
│   │   └── landing_page.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── advocate_service.py
│   │   ├── case_service.py
│   │   ├── document_service.py   # S3 upload/download
│   │   ├── draft_service.py     # AI drafting (Qwen3-VL)
│   │   ├── compliance_service.py # AIPOT-COMPLIANCE
│   │   ├── scraper_service.py   # AIPOT-SCRAPER
│   │   ├── communicator_service.py # AIPOT-COMMUNICATOR
│   │   ├── reminder_service.py
│   │   ├── invoice_service.py
│   │   ├── payment_service.py   # Razorpay
│   │   ├── whatsapp_service.py  # 360dialog
│   │   ├── sms_service.py       # MSG91
│   │   ├── email_service.py     # SendGrid
│   │   ├── voice_service.py    # AI24x7 TTS
│   │   ├── translation_service.py # AIPOT-TRANSLATE
│   │   ├── research_service.py # AIPOT-RESEARCH (pgvector)
│   │   ├── notification_service.py
│   │   ├── police_service.py   # AIPOT-POLICE
│   │   └── billing_service.py  # AIPOT-BILLING
│   │
│   └── utils/
│       ├── __init__.py
│       ├── storage.py          # S3/R2 operations
│       ├── otp.py              # OTP generation
│       ├── case_number.py      # CNR format validator
│       ├── invoice_pdf.py      # WeasyPrint PDF generation
│       ├── embeddings.py       # pgvector embeddings
│       └── helpers.py
│
├── celery_app/
│   ├── __init__.py
│   ├── celery.py
│   └── tasks/
│       ├── __init__.py
│       ├── scraper_tasks.py
│       ├── reminder_tasks.py
│       ├── draft_tasks.py
│       ├── translate_tasks.py
│       ├── voice_tasks.py
│       └── cleanup_tasks.py
│
├── scripts/
│   ├── seed_forms.py          # Seed legal form templates
│   ├── seed_checklists.py      # Seed court checklists
│   └── create_super_admin.py
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_cases.py
│   ├── test_drafts.py
│   └── test_scraper.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml          # API + Worker + Kafka + Redis
└── README.md
```

---

## Key API Routes

### Auth: `/api/v1/auth`
```
POST /auth/register          # Advocate registration
POST /auth/login             # Login (returns JWT)
POST /auth/verify-email-otp  # Email OTP verify
POST /auth/verify-phone-otp  # WhatsApp OTP verify
POST /auth/forgot-password
POST /auth/reset-password
POST /auth/refresh-token
POST /auth/logout
GET  /auth/me               # Current user
PUT  /auth/me               # Update profile
PUT  /auth/me/password      # Change password
```

### Advocates: `/api/v1/advocates`
```
GET  /advocates/me          # My profile
PUT  /advocates/me          # Update profile
GET  /advocates/team       # Team members (advocate admin only)
POST /advocates/invite      # Invite team member
GET  /advocates/invites     # Pending invites
DELETE /advocates/invites/{id}  # Revoke invite
GET  /advocates/stats       # Dashboard stats
Admin:
GET  /advocates             # All advocates (super admin)
PUT  /advocates/{id}/plan   # Change plan
```

### Cases: `/api/v1/cases`
```
GET  /cases                 # List my cases (filterable)
POST /cases                 # Create case
GET  /cases/{id}            # Case detail
PUT  /cases/{id}            # Update case
DELETE /cases/{id}          # Soft delete case
GET  /cases/{id}/timeline  # Status history
GET  /cases/{id}/documents # Documents list
GET  /cases/{id}/orders    # Court orders
GET  /cases/{id}/drafts    # AI drafts
GET  /cases/{id}/tasks     # Tasks
GET  /cases/upcoming       # Cases with next hearing (calendar)
Admin:
PUT  /cases/{id}/assign    # Assign to advocate
```

### Drafts (AI): `/api/v1/drafts`
```
POST /drafts                # Generate AI draft (AIPOT-DRAFT)
GET  /drafts                # List my drafts
GET  /drafts/{id}          # Draft detail
PUT  /drafts/{id}          # Edit draft
POST /drafts/{id}/approve  # Advocate approves
POST /drafts/{id}/reject   # Reject
POST /drafts/{id}/compliance  # Run AIPOT-COMPLIANCE check
GET  /drafts/{id}/suggestions  # AI suggestions
```

### Court Orders: `/api/v1/court-orders`
```
GET  /court-orders         # List (filterable by case, court, date)
GET  /court-orders/{id}    # Order detail
GET  /court-orders/{id}/summary  # AI summary
POST /court-orders/scrape   # Trigger manual scrape (AIPOT-SCRAPER)
GET  /courts                # List supported courts
```

### Documents: `/api/v1/documents`
```
POST /documents/upload     # Upload document (multipart)
GET  /documents/{id}       # Document detail
GET  /documents/{id}/download  # Presigned download URL
PUT  /documents/{id}       # Update metadata
DELETE /documents/{id}     # Soft delete
POST /documents/{id}/verify # Mark verified (admin)
```

### Payments: `/api/v1/payments`
```
POST /payments/initiate    # Create Razorpay order
POST /payments/confirm     # Confirm payment
POST /payments/webhook     # Razorpay webhook
GET  /payments/{id}
GET  /payments/history
```

### Reminders: `/api/v1/reminders`
```
GET  /reminders            # My scheduled reminders
POST /reminders            # Create reminder
PUT  /reminders/{id}       # Update
DELETE /reminders/{id}     # Cancel
GET  /reminders/upcoming   # Next 7 days
```

### Admin: `/api/v1/admin`
```
GET  /admin/dashboard      # Super admin stats
GET  /admin/advocates      # All advocate accounts
GET  /admin/cases          # All cases across tenants
GET  /admin/invoices       # All invoices
GET  /admin/communications # All comms log
POST /admin/subscriptions  # Create subscription
PUT  /admin/plans          # Update pricing
GET  /admin/audit-logs    # System audit log
```

---

## Multi-Tenant Setup (Critical)

```python
# app/core/tenant.py
from contextvars import ContextVar
tenant_id: ContextVar[UUID | None] = ContextVar("tenant_id", default=None)

# In FastAPI middleware (app/main.py):
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    if token := request.headers.get("Authorization"):
        payload = decode_jwt(token.replace("Bearer ", ""))
        tenant_id.set(payload.get("tenant_id"))
    response = await call_next(request)
    return response

# Usage in any query:
def get_cases(db: AsyncSession, tenant_id: UUID):
    result = await db.execute(
        select(Case).where(Case.tenant_id == tenant_id)  # RLS enforced
    )
```

---

## Kafka Topics

```
letese.scraper.jobs          # Court scraping jobs
letese.scraper.orders        # New orders found
letese.draft.generated       # AI draft completed
letese.reminder.schedules    # Reminder dispatch
letese.comm.whatsapp         # WhatsApp message queue
letese.comm.email            # Email queue
letese.comm.sms              # SMS queue
letese.comm.voice            # Voice call queue
letese.payment.webhooks      # Payment webhook events
```

---

## Environment Variables

```env
# App
APP_ENV=development
SECRET_KEY=<32-char-random>
FRONTEND_URL=https://app.letese.xyz

# Database (existing)
DATABASE_URL=postgresql+asyncpg://postgres:password@187.127.139.147:5433/ai_drafting
REDIS_URL=redis://187.127.139.147:6379/0

# Kafka
KAFKA_BOOTSTRAP_SERVERS=43.242.224.231:9092

# AI Server (existing)
AI24X7_API_URL=http://43.242.224.231:8080
AI24X7_API_KEY=<key-if-required>

# Razorpay
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=

# WhatsApp (360dialog)
W360_API_KEY=
W360_WABA_ID=

# SMS (MSG91)
MSG91_AUTH_KEY=
MSG91_SENDER_ID=LETESE

# Email (SendGrid)
SENDGRID_API_KEY=
FROM_EMAIL=noreply@letese.co

# File Storage (Local S3-like)
STORAGE_BASE_PATH=/data/letese-docs
```
