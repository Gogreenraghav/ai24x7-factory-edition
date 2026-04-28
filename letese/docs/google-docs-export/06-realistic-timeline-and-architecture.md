# LETESE — Realistic Timeline, Architecture & Complete Project Plan
> Deep Planning Document | Date: 27 April 2026 | Version: 1.0

---

## Executive Summary

**Total Time for Full v1.0:** 90 Days (Realistic)  
**Minimum Viable Product (MVP):** 45 Days  
**Team假设:** 1 developer (Arjun) + AI assistant (me)

> ⚠️ 60-day plan mentioned earlier was optimistic. Real engineering needs 90 days for production-quality system that handles billions of records smoothly.

---

## The Big Picture — What We're Building

LETESE is a **multi-tenant SaaS** with these layers:

```
┌─────────────────────────────────────────────────────────┐
│                    USER LAYER                          │
│  Super Admin │ Advocate │ Clerk │ Client (7 roles)      │
└──────────────────────┬────────────────────────────────┘
                       │
┌──────────────────────▼────────────────────────────────┐
│                 FRONTEND LAYER                         │
│  admin.letese.xyz │ app.letese.xyz │ client.letese.xyz │
│  (React + FlutterFlow)                                 │
└──────────────────────┬────────────────────────────────┘
                       │
┌──────────────────────▼────────────────────────────────┐
│               API GATEWAY LAYER                        │
│  FastAPI + JWT auth + Rate limiting + Tenant isolation  │
└──────────────────────┬────────────────────────────────┘
                       │
┌──────────────────────▼────────────────────────────────┐
│              SERVICE / AGENT LAYER                     │
│  8 AIPOT Agents + Business Logic                      │
│  (FastAPI services, Celery workers, Kafka consumers)   │
└──────────────────────┬────────────────────────────────┘
                       │
┌──────────────────────▼────────────────────────────────┐
│               DATA / AI LAYER                          │
│  PostgreSQL + pgvector │ Redis │ S3 │ AI24x7 GPU      │
└─────────────────────────────────────────────────────────┘
```

---

## Architecture for Billions of Records (Scale)

### Problem: Most SaaS crashes when data grows
- 1 firm = 10,000 cases
- 100 firms = 1,000,000 cases
- 10,000 firms = 100,000,000 cases

**Solution: Sharding + Partitioning + Smart Caching**

### Database Strategy (PostgreSQL at scale)

```
PostgreSQL: 187.127.139.147:5433
│
├── Partitioning by TENANT (logical)
│   Each tenant's data isolated via RLS + separate schemas
│
├── Table Partitioning (for cases, orders, logs)
│   cases table partitioned by RANGE on created_at
│   e.g., cases_2026_q1, cases_2026_q2, etc.
│
├── Indexes on critical columns
│   cases: (tenant_id, cnr_number) UNIQUE
│   cases: (tenant_id, hearing_date) 
│   court_orders: (cnr, scraped_at) 
│   communications: (tenant_id, sent_at) 
│
└── pgvector for semantic search
    Embeddings stored separately, queried with IVFFlat/HNSW
```

### AI Server Strategy (Handle millions of AI calls)
```
43.242.224.231:8080 (AI24x7 Qwen3-VL)
│
├── llama-server with context window management
│   Max 2048 tokens per request (control costs)
│
├── Celery task queue (parallel AI requests)
│   5 Celery workers = 5 parallel AI calls
│   Queue: Redis at 187.127.139.147:6379
│
├── Request batching
│   Batch similar requests together = faster + cheaper
│
└── Response caching
│   Same prompt = cached response (Redis, 1-hour TTL)
│
└── GPU memory management
    Keep model loaded, don't reload per request
    (currently 6.8GB used / 23GB = 16GB headroom ✅)
```

### Caching Strategy (Redis)
```
Redis: 187.127.139.147:6379
│
├── Session cache: session:{tenant_id}:{user_id} → JWT data
│   TTL: 24 hours
│
├── AI response cache: ai:cache:{sha256(prompt)} → response
│   TTL: 1 hour
│
├── Rate limiting: ratelimit:{tenant_id}:{endpoint}
│   Sliding window, 100 req/min
│
├── Scraper dedup: scraper:seen:{hash} → timestamp
│   Prevents duplicate orders
│
└── Session tokens: token:{jti} → {user_id, tenant_id, role}
    TTL: matches JWT expiry
```

### File Storage Strategy (S3 / Local)
```
Storage: 43.242.224.231 (local disk for MVP)
│
├── s3://letese-docs/{tenant_id}/{year}/{month}/
│   Documents organized by tenant + date
│
├── Max file size: 50MB (enforced in API)
│
├── Presigned URLs (no direct S3 access)
│   Download link valid: 15 minutes
│
├── CDN: CloudFlare in front
│   Static assets cached globally
│
└── Backup: Daily snapshots to secondary server
```

---

## Complete System Architecture Diagram

```
                    ┌─────────────────────────┐
                    │    USERS (7 roles)     │
                    └───────────┬─────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
    ┌─────▼──────┐      ┌──────▼──────┐     ┌───────▼───────┐
    │   ADMIN    │      │   ADVOCATE  │     │    CLIENT     │
    │  Portal    │      │   App       │     │   Portal      │
    │ admin.     │      │ app.        │     │ {firm}.       │
    │ letese.xyz │      │ letese.xyz  │     │ letese.xyz    │
    └─────┬──────┘      └──────┬──────┘     └───────┬───────┘
          │                     │                     │
          └─────────────────────┼─────────────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │    CLOUDFLARE CDN       │
                    │  (SSL + Caching + WAF)  │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │    FastAPI Backend      │
                    │   (43.242.224.231)      │
                    │  Port: 4001 (REST API)  │
                    │  Port: 4002 (WebSocket) │
                    └───────────┬─────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼───────┐     ┌────────▼────────┐    ┌─────────▼─────────┐
│  Celery       │     │   FastAPI       │    │   Kafka           │
│  Workers      │     │   Services      │    │   (Message Queue) │
│  (Background) │     │                 │    │   43.242.224.231  │
│  Port: 4003   │     │                 │    │                   │
└───────┬───────┘     └────────┬────────┘    └─────────┬─────────┘
        │                      │                       │
        │         ┌────────────┼────────────┐          │
        │         │            │            │          │
        │    ┌────▼────┐  ┌────▼────┐  ┌───▼────┐   ┌──▼──────────┐
        │    │Redis    │  │AI Server│  │S3/File │   │Court Portals│
        │    │Cache    │  │Qwen3-VL │  │Storage │   │(Scraper)    │
        │    │Queue    │  │:8080    │  │        │   └────────────┘
        │    └─────────┘  └─────────┘  └────────┘
        │
        │  ┌──────────────────────────────────┐
        └──│        PostgreSQL                │
           │   (187.127.139.147:5433)        │
           │   pgvector + RLS + Partitioning  │
           │   ai_drafting database          │
           └──────────────────────────────────┘
```

---

## The 8 AIPOT Agents — Technical Design

### How They Work Together

```
Advocate creates a case
         │
         ▼
┌─────────────────────────────────────────┐
│         AIPOT-COMMUNICATOR              │
│  Schedule reminders: 15d, 7d, 48h, 24h  │
│  (Celery beat tasks)                    │
└────────────────┬────────────────────────┘
                 │
    Every 15 min (Kafka triggered)
         │
         ▼
┌─────────────────────────────────────────┐
│           AIPOT-SCRAPER                  │
│  Check court portals for new orders     │
│  (Playwright + rotating proxies)         │
│  Match CNR → existing case?              │
└────────────────┬────────────────────────┘
                 │ New order found
                 ▼
┌─────────────────────────────────────────┐
│        AIPOT-COMMUNICATOR                │
│  Send WhatsApp/SMS: "New order in       │
│  your case XYZ"                          │
└────────────────┬────────────────────────┘
                 │
         (Advocate clicks "Generate Draft")
                 │
                 ▼
┌─────────────────────────────────────────┐
│            AIPOT-DRAFT                   │
│  Call AI24x7 Qwen3-VL                   │
│  Generate petition in 5 minutes         │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         AIPOT-COMPLIANCE                 │
│  Run 7 validation checks                │
│  Return score + suggestions              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         AIPOT-BILLING                    │
│  If invoice needed → Razorpay            │
│  GST invoice → PDF → S3 → Email         │
└─────────────────────────────────────────┘
```

---

## Realistic Timeline — 90 Days (12 Weeks)

### Phase 0 — Foundation Setup (Days 1-7)
> Setup everything before writing a single line of business logic

| Day | Task | Status |
|-----|------|--------|
| 1-2 | Provision servers, install Docker, setup Docker Compose | 🔲 |
| 1-2 | PostgreSQL schema redesign (fix pricing, add missing tables) | 🔲 |
| 1-3 | Design database migrations (Alembic) | 🔲 |
| 3-4 | FastAPI project scaffold (file structure, config, logging) | 🔲 |
| 4-5 | JWT authentication (signup/login/refresh/logout) | 🔲 |
| 5-7 | Tenant isolation middleware (RLS + JWT tenant_id) | 🔲 |
| 6-7 | Database connection pooling (SQLAlchemy async + pgBouncer) | 🔲 |
| 7 | **Milestone:** Auth + DB ready, can create tenant + user | ✅ |

### Phase 1A — Core Backend (Days 8-21)
> Case management, documents, hearings — the heart of the system

| Day | Task | Deliverable |
|-----|------|-------------|
| 8-10 | Cases CRUD API | POST/GET/PUT/DELETE /api/cases |
| 10-12 | Case parties API | Plaintiff, defendant, advocate links |
| 12-14 | Hearings API + scheduler | Hearing dates + auto-reminder setup |
| 14-16 | Documents upload/download | S3 + presigned URLs |
| 16-18 | Tenant admin settings | Firm profile, team management |
| 18-20 | Roles & permissions (RBAC) | Advocate/Clerk/Paralegal/Intern/Client |
| 21 | **Milestone:** Full case lifecycle API working | ✅ |

### Phase 1B — Frontend MVP (Days 15-30) [PARALLEL]
> Advocates need to SEE data, not just have API

| Day | Task | Deliverable |
|-----|------|-------------|
| 15-17 | FlutterFlow setup + API connection | Login screen + token storage |
| 18-20 | Dashboard home (stats cards, recent cases) | Real data from API |
| 20-22 | Case list + case detail page | Full CRUD from frontend |
| 23-25 | Document upload UI | File picker + progress bar |
| 25-27 | Hearing calendar view | Calendar with hearing dates |
| 28-30 | Team management UI | Add/edit team members |
| 30 | **Milestone:** Advocate can use app end-to-end | ✅ |

### Phase 2 — 4 AIPOT Agents + Integrations (Days 22-50)

#### AIPOT-COMPLIANCE + AIPOT-DRAFT (Days 22-35)
| Day | Task | Deliverable |
|-----|------|-------------|
| 22-25 | Connect AI24x7 Qwen3-VL API | `/v1/chat/completions` call |
| 25-28 | AIPOT-DRAFT service | Prompt engineering for petitions |
| 28-30 | Draft approval workflow | Save → review → approve → file |
| 30-33 | AIPOT-COMPLIANCE service | 7 validation checks |
| 33-35 | Draft history + version control | Compare draft versions |
| 35 | **Milestone:** AI drafting works end-to-end | ✅ |

#### AIPOT-COMMUNICATOR (Days 36-42)
| Day | Task | Deliverable |
|-----|------|-------------|
| 36-38 | 360dialog WhatsApp setup | WhatsApp Business API connected |
| 38-40 | Celery beat scheduler | 15d/7d/48h/24h reminder triggers |
| 40-42 | Multi-channel sender | WhatsApp + SMS + Email + Voice |
| 42 | **Milestone:** Auto-reminders working | ✅ |

#### AIPOT-SCRAPER (Days 43-50)
| Day | Task | Deliverable |
|-----|------|-------------|
| 43-45 | Kafka setup + topics | `letese.scraper.jobs` topic |
| 45-47 | P&H HC scraper (priority) | Playwright + CNR parsing |
| 47-49 | Delhi HC scraper | Second court connected |
| 49-50 | Order matching + alerts | Match CNR → case → notify |
| 50 | **Milestone:** Court orders auto-detected | ✅ |

### Phase 3 — Billing + Research + Translate (Days 51-65)

#### AIPOT-BILLING (Days 51-56)
| Day | Task | Deliverable |
|-----|------|-------------|
| 51-53 | Razorpay integration | Payment links + webhook |
| 53-55 | Invoice generation | WeasyPrint PDF + GST 18% |
| 55-56 | Subscription management | Upgrade/downgrade/cancel |
| 56 | **Milestone:** Paid subscriptions work | ✅ |

#### AIPOT-RESEARCH + AIPOT-TRANSLATE + AIPOT-POLICE (Days 57-65)
| Day | Task | Deliverable |
|-----|------|-------------|
| 57-59 | pgvector setup | Embedding generation pipeline |
| 59-61 | Semantic search UI | Query + top 10 results |
| 61-63 | Meta MMS translation | EN/HI/PA with format preserve |
| 63-65 | AIPOT-POLICE health checks | Slack/SMS alerts if down |
| 65 | **Milestone:** All 8 AIPOTs functional | ✅ |

### Phase 4 — Super Admin + Client Portal (Days 66-78)

#### Super Admin Dashboard (admin.letese.xyz) (Days 66-72)
| Day | Task | Deliverable |
|-----|------|-------------|
| 66-68 | Tenant management | View all tenants, suspend, delete |
| 68-70 | Usage analytics | Cases per tenant, AI usage, revenue |
| 70-72 | System config | Pricing, email templates, WhatsApp templates |
| 72 | **Milestone:** Super admin controls everything | ✅ |

#### Client White-Label Portal (Days 73-78)
| Day | Task | Deliverable |
|-----|------|-------------|
| 73-75 | Branded subdomain routing | `{firm}.letese.xyz` |
| 75-77 | Client dashboard | Own case status + documents |
| 77-78 | Client notification preferences | Email/SMS/WhatsApp toggle |
| 78 | **Milestone:** Clients can self-serve | ✅ |

### Phase 5 — Hardening + Launch (Days 79-90)

| Day | Task | Deliverable |
|-----|------|-------------|
| 79-81 | Load testing | k6 scripts, 1000 concurrent users |
| 81-83 | Security audit | SQL injection, XSS, RBAC bypass tests |
| 83-85 | Performance optimization | DB indexes, Redis cache, query优化 |
| 85-87 | Documentation | API docs (Swagger), admin guide, user guide |
| 87-89 | Deployment | Docker compose, CI/CD pipeline, monitoring |
| 90 | **LAUNCH DAY** | v1.0 live at letese.xyz |

---

## Critical Path — What to Build in What Order

```
Day 1 ─────────────────────────────────────────────────── Day 90
│
├── Phase 0 (Setup) ── Phase 1 ── Phase 2 ── Phase 3 ── Phase 4 ── Phase 5
│
CRITICAL PATH (must happen in order):
1. DB schema → 2. Auth → 3. Cases API → 4. Flutter app → 5. AI Drafting
                                                                              │
                                                              ↓
Without #5, nothing to sell. Without #3+4, nothing to demo.
Without #1+2, nothing works.

PARALLEL TRACKS:
• Backend API team: Phase 0 → Phase 1A → Phase 2 → Phase 3
• Frontend team: FlutterFlow setup → Connect API → Build screens
• DevOps: Docker, monitoring, CI/CD (from Day 1)
```

---

## Database Design for Scale (25 Tables)

### Core Tables
```sql
-- Multi-tenant root table
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    subdomain TEXT UNIQUE NOT NULL,
    plan TEXT DEFAULT 'basic',  -- basic|professional|elite|enterprise
    case_limit INTEGER DEFAULT 30,
    storage_used_bytes BIGINT DEFAULT 0,
    storage_limit_bytes BIGINT DEFAULT 5368709120,  -- 5GB
    razorpay_customer_id TEXT,
    razorpay_subscription_id TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Users within a tenant
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    email TEXT NOT NULL,
    phone TEXT,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,  -- advocate_admin|advocate|clerk|paralegal|intern|client
    bar_council_no TEXT,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Cases (partitioned by created_at)
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    cnr_number TEXT,
    case_no TEXT NOT NULL,
    court_name TEXT NOT NULL,
    case_type TEXT,
    subject TEXT,
    description TEXT,
    status TEXT DEFAULT 'active',  -- active|closed|pending|disposed
    priority TEXT DEFAULT 'normal',
    next_hearing_date DATE,
    judge_name TEXT,
    opposing_party_name TEXT,
    opposing_counsel TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Hearings
CREATE TABLE hearings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    case_id UUID REFERENCES cases(id),
    hearing_date DATE NOT NULL,
    hearing_time TIME,
    court_name TEXT,
    purpose TEXT,
    order_url TEXT,
    reminder_15d BOOLEAN DEFAULT false,
    reminder_7d BOOLEAN DEFAULT false,
    reminder_48h BOOLEAN DEFAULT false,
    reminder_24h BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Court orders (scraped) — HIGH VOLUME table
CREATE TABLE court_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    case_id UUID REFERENCES cases(id),  -- NULL if no match
    cnr_number TEXT,
    court_name TEXT,
    order_date DATE,
    order_text TEXT,
    order_hash TEXT,  -- SHA256 for dedup
    pdf_url TEXT,
    scraped_at TIMESTAMPTZ DEFAULT now()
);

-- Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    case_id UUID REFERENCES cases(id),
    uploaded_by UUID REFERENCES users(id),
    file_name TEXT NOT NULL,
    file_type TEXT,
    file_size_bytes BIGINT,
    s3_key TEXT,
    storage_path TEXT,
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT now()
);

-- AI Drafts
CREATE TABLE drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    case_id UUID REFERENCES cases(id),
    created_by UUID REFERENCES users(id),
    petition_type TEXT NOT NULL,
    language TEXT DEFAULT 'en',
    prompt TEXT,
    response_text TEXT,
    compliance_score NUMERIC(5,2),
    compliance_report JSONB,
    status TEXT DEFAULT 'draft',  -- draft|approved|filed|rejected
    file_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Communications log (HIGH VOLUME — billions of rows)
CREATE TABLE communications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    case_id UUID REFERENCES cases(id),
    user_id UUID REFERENCES users(id),
    channel TEXT NOT NULL,  -- whatsapp|sms|email|voice
    direction TEXT NOT NULL,  -- outbound|inbound
    template_name TEXT,
    message TEXT,
    status TEXT,  -- sent|failed|delivered|read
    external_id TEXT,  -- Provider message ID
    sent_at TIMESTAMPTZ DEFAULT now()
);

-- Invoices
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    invoice_no TEXT UNIQUE NOT NULL,  -- LETESE.INV-2026-00001
    amount DECIMAL(10,2) NOT NULL,
    gst_percent NUMERIC(5,2) DEFAULT 18.0,
    gst_amount DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending|paid|overdue|cancelled
    razorpay_order_id TEXT,
    razorpay_payment_id TEXT,
    paid_at TIMESTAMPTZ,
    due_date DATE,
    invoice_pdf_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    plan TEXT NOT NULL,
    status TEXT DEFAULT 'active',  -- active|trial|cancelled|past_due
    started_at TIMESTAMPTZ DEFAULT now(),
    ends_at TIMESTAMPTZ,
    auto_recharge BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- AI suggestions (from AIPOT-COMPLIANCE)
CREATE TABLE ai_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    draft_id UUID REFERENCES drafts(id),
    check_type TEXT,
    status TEXT,  -- pass|warning|error
    score NUMERIC(5,2),
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Translation jobs
CREATE TABLE translation_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    document_id UUID REFERENCES documents(id),
    source_lang TEXT NOT NULL,
    target_lang TEXT NOT NULL,
    accuracy_score NUMERIC(5,2),
    status TEXT DEFAULT 'pending',  -- pending|processing|completed|failed
    translated_file_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Scraper jobs (Kafka checkpoint)
CREATE TABLE scraper_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    court_name TEXT NOT NULL,
    last_scrape_at TIMESTAMPTZ,
    last_success_at TIMESTAMPTZ,
    orders_found INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',  -- active|paused|error
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- System health log (AIPOT-POLICE)
CREATE TABLE system_health (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    check_name TEXT NOT NULL,
    status TEXT,  -- healthy|warning|critical
    response_time_ms INTEGER,
    error_message TEXT,
    checked_at TIMESTAMPTZ DEFAULT now()
);
```

---

## API Design — All Endpoints

### Authentication
```
POST /api/v1/auth/register      — Create tenant + first user
POST /api/v1/auth/login         — Login, return JWT
POST /api/v1/auth/refresh       — Refresh access token
POST /api/v1/auth/logout        — Invalidate session
POST /api/v1/auth/verify-email  — Email OTP verification
POST /api/v1/auth/verify-phone  — WhatsApp OTP verification
GET  /api/v1/auth/me            — Current user profile
PUT  /api/v1/auth/me           — Update profile
```

### Cases
```
GET    /api/v1/cases            — List cases (paginated, filtered)
POST   /api/v1/cases            — Create case
GET    /api/v1/cases/{id}       — Get case detail
PUT    /api/v1/cases/{id}       — Update case
DELETE /api/v1/cases/{id}       — Soft delete case
GET    /api/v1/cases/{id}/timeline — Case history
POST   /api/v1/cases/{id}/parties  — Add party to case
```

### Hearings
```
GET    /api/v1/hearings         — List hearings
POST   /api/v1/hearings         — Create hearing
GET    /api/v1/hearings/{id}    — Get hearing
PUT    /api/v1/hearings/{id}    — Update hearing
DELETE /api/v1/hearings/{id}    — Delete hearing
GET    /api/v1/hearings/upcoming — Hearings in next 7 days
```

### Documents
```
POST   /api/v1/documents/upload — Upload file (multipart)
GET    /api/v1/documents/{id}   — Download file (presigned URL)
DELETE /api/v1/documents/{id}   — Delete file
GET    /api/v1/documents        — List documents (filtered by case)
```

### AI Drafts (AIPOT-DRAFT)
```
POST   /api/v1/drafts/generate  — Generate AI petition
GET    /api/v1/drafts           — List drafts
GET    /api/v1/drafts/{id}      — Get draft + compliance report
PUT    /api/v1/drafts/{id}      — Edit draft
POST   /api/v1/drafts/{id}/approve — Approve draft
POST   /api/v1/drafts/{id}/reject  — Reject draft
GET    /api/v1/drafts/templates — List petition templates
```

### Court Orders (AIPOT-SCRAPER)
```
GET    /api/v1/courts           — List supported courts
GET    /api/v1/orders          — List scraped orders
GET    /api/v1/orders/{id}     — Get order detail
POST   /api/v1/scraper/trigger  — Manually trigger scraper
GET    /api/v1/scraper/status   — Scraper health
```

### Communications (AIPOT-COMMUNICATOR)
```
POST   /api/v1/communications/send  — Send WhatsApp/SMS/Email
GET    /api/v1/communications        — Message history
POST   /api/v1/communications/webhook — Provider webhook receiver
PUT    /api/v1/reminders/preferences  — Notification preferences
```

### Billing (AIPOT-BILLING)
```
POST   /api/v1/billing/create-invoice — Create invoice
GET    /api/v1/billing/invoices      — List invoices
GET    /api/v1/billing/invoices/{id} — Invoice detail
POST   /api/v1/billing/payment-link   — Generate Razorpay link
POST   /api/v1/billing/webhook        — Razorpay webhook
GET    /api/v1/billing/subscription   — Current plan
POST   /api/v1/billing/upgrade        — Upgrade plan
POST   /api/v1/billing/cancel         — Cancel subscription
```

### Research (AIPOT-RESEARCH)
```
POST   /api/v1/research/search  — Semantic search
GET    /api/v1/research/history  — Past searches
GET    /api/v1/research/precedents — Saved precedents
```

### Translation (AIPOT-TRANSLATE)
```
POST   /api/v1/translate         — Translate document
GET    /api/v1/translate/{id}   — Check status + download
GET    /api/v1/translate/languages — Supported language pairs
```

### Admin (Super Admin only)
```
GET    /api/v1/admin/tenants     — List all tenants
POST   /api/v1/admin/tenants     — Create tenant manually
GET    /api/v1/admin/tenants/{id} — Tenant detail + usage
PUT    /api/v1/admin/tenants/{id} — Update tenant (plan, status)
DELETE /api/v1/admin/tenants/{id} — Suspend tenant
GET    /api/v1/admin/usage       — System-wide usage stats
GET    /api/v1/admin/revenue     — Revenue analytics
GET    /api/v1/admin/health      — System health (AIPOT-POLICE)
```

---

## Scalability Architecture — How to Handle Growth

### Current capacity vs future needs
```
TODAY (Day 1):
- 1-10 tenants
- 1,000 cases
- 100 AI requests/day
→ Single server (43.242.224.231) handles everything

YEAR 1 (100 tenants):
- 100 tenants
- 100,000 cases
- 10,000 AI requests/day
→ Need: read replicas, more Celery workers

YEAR 2 (1,000 tenants):
- 1,000 tenants
- 1,000,000 cases
- 100,000 AI requests/day
→ Need: horizontal scaling, Kafka partitioning, CDN

YEAR 3+ (10,000+ tenants):
- 10,000+ tenants
- 100,000,000 cases
- 1,000,000+ AI requests/day
→ Need: database sharding, GPU cluster, microservices
```

### Horizontal Scaling Strategy
```
Load Balancer (CloudFlare → Nginx)
        │
        ├── API Server 1 (43.242.224.231:4001)
        ├── API Server 2 (43.242.224.232:4001)  ← new server
        └── API Server 3 (43.242.224.233:4001)  ← new server

Celery Workers:
        ├── Worker 1-5: Draft generation (GPU tasks)
        ├── Worker 6-10: Court scraper (I/O tasks)
        ├── Worker 11-15: Communications (API calls)
        └── Worker 16-20: Billing/reporting (CPU tasks)

PostgreSQL:
        ├── Primary: writes (187.127.139.147)
        ├── Replica 1: reads (same machine for MVP)
        └── Replica 2: reads (new server) → Year 2
```

---

## File Structure (Complete Backend)

```
letese-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app, lifespan events
│   ├── config.py                  # Settings from env vars
│   ├── database.py                # Async SQLAlchemy session
│   ├── redis_client.py            # Redis connection
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── tenant.py
│   │   ├── user.py
│   │   ├── case.py
│   │   ├── hearing.py
│   │   ├── document.py
│   │   ├── draft.py
│   │   ├── court_order.py
│   │   ├── communication.py
│   │   ├── invoice.py
│   │   ├── subscription.py
│   │   ├── ai_suggestion.py
│   │   ├── translation_job.py
│   │   ├── scraper_job.py
│   │   └── system_health.py
│   ├── schemas/                   # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── case.py
│   │   ├── hearing.py
│   │   ├── document.py
│   │   ├── draft.py
│   │   ├── billing.py
│   │   └── common.py
│   ├── routers/                   # FastAPI route modules
│   │   ├── __init__.py
│   │   ├── auth.py               # /api/v1/auth/*
│   │   ├── cases.py              # /api/v1/cases/*
│   │   ├── hearings.py           # /api/v1/hearings/*
│   │   ├── documents.py          # /api/v1/documents/*
│   │   ├── drafts.py             # /api/v1/drafts/*
│   │   ├── courts.py             # /api/v1/courts/*
│   │   ├── communications.py      # /api/v1/communications/*
│   │   ├── billing.py            # /api/v1/billing/*
│   │   ├── research.py           # /api/v1/research/*
│   │   ├── translate.py          # /api/v1/translate/*
│   │   └── admin.py              # /api/v1/admin/*
│   ├── services/                 # Business logic (pure Python)
│   │   ├── auth_service.py       # JWT, password hashing
│   │   ├── ai_service.py         # AI24x7 Qwen3-VL API client
│   │   ├── whatsapp_service.py   # 360dialog API client
│   │   ├── sms_service.py        # MSG91 API client
│   │   ├── email_service.py      # SendGrid API client
│   │   ├── razorpay_service.py   # Razorpay API client
│   │   ├── storage_service.py    # S3 / local file ops
│   │   ├── embed_service.py      # Sentence transformers (pgvector)
│   │   └── notification_service