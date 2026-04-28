━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART 6: Realistic Timeline & Architecture
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LETESE — Realistic Timeline, Architecture & Complete Project Plan
> Deep Planning Document | Date: 27 April 2026 | Version: 1.0
Executive Summary
**Total Time for Full v1.0:** 90 Days (Realistic)  
**Minimum Viable Product (MVP):** 45 Days  
**Team假设:** 1 developer (Arjun) + AI assistant (me)
> ⚠️ 60-day plan mentioned earlier was optimistic. Real engineering needs 90 days for production-quality system that handles billions of records smoothly.
The Big Picture — What We're Building
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
Architecture for Billions of Records (Scale)
Problem: Most SaaS crashes when data grows
- 1 firm = 10,000 cases
- 100 firms = 1,000,000 cases
- 10,000 firms = 100,000,000 cases
**Solution: Sharding + Partitioning + Smart Caching**
Database Strategy (PostgreSQL at scale)
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
AI Server Strategy (Handle millions of AI calls)
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
Caching Strategy (Redis)
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
File Storage Strategy (S3 / Local)
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
Complete System Architecture Diagram
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
The 8 AIPOT Agents — Technical Design
How They Work Together
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
Realistic Timeline — 90 Days (12 Weeks)
Phase 0 — Foundation Setup (Days 1-7)
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
Phase 1A — Core Backend (Days 8-21)
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
Phase 1B — Frontend MVP (Days 15-30) [PARALLEL]
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
Phase 2 — 4 AIPOT Agents + Integrations (Days 22-50)
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
Phase 3 — Billing + Research + Translate (Days 51-65)
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
Phase 4 — Super Admin + Client Portal (Days 66-78)
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
Phase 5 — Hardening + Launch (Days 79-90)
| Day | Task | Deliverable |
|-----|------|-------------|
| 79-81 | Load testing | k6 scripts, 1000 concurrent users |
| 81-83 | Security audit | SQL injection, XSS, RBAC bypass tests |
| 83-85 | Performance optimization | DB indexes, Redis cache, query优化 |
| 85-87 | Documentation | API docs (Swagger), admin guide, user guide |
| 87-89 | Deployment | Docker compose, CI/CD pipeline, monitoring |
| 90 | **LAUNCH DAY** | v1.0 live at letese.xyz |
Critical Path — What to Build in What Order
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
Database Design for Scale (25 Tables)
Core Tables
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
API Design — All Endpoints
Authentication
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
Cases
```
GET    /api/v1/cases            — List cases (paginated, filtered)
POST   /api/v1/cases            — Create case
GET    /api/v1/cases/{id}       — Get case detail
PUT    /api/v1/cases/{id}       — Update case
DELETE /api/v1/cases/{id}       — Soft delete case
GET    /api/v1/cases/{id}/timeline — Case history
POST   /api/v1/cases/{id}/parties  — Add party to case
```
Hearings
```
GET    /api/v1/hearings         — List hearings
POST   /api/v1/hearings         — Create hearing
GET    /api/v1/hearings/{id}    — Get hearing
PUT    /api/v1/hearings/{id}    — Update hearing
DELETE /api/v1/hearings/{id}    — Delete hearing
GET    /api/v1/hearings/upcoming — Hearings in next 7 days
```
Documents
```
POST   /api/v1/documents/upload — Upload file (multipart)
GET    /api/v1/documents/{id}   — Download file (presigned URL)
DELETE /api/v1/documents/{id}   — Delete file
GET    /api/v1/documents        — List documents (filtered by case)
```
AI Drafts (AIPOT-DRAFT)
```
POST   /api/v1/drafts/generate  — Generate AI petition
GET    /api/v1/drafts           — List drafts
GET    /api/v1/drafts/{id}      — Get draft + compliance report
PUT    /api/v1/drafts/{id}      — Edit draft
POST   /api/v1/drafts/{id}/approve — Approve draft
POST   /api/v1/drafts/{id}/reject  — Reject draft
GET    /api/v1/drafts/templates — List petition templates
```
Court Orders (AIPOT-SCRAPER)
```
GET    /api/v1/courts           — List supported courts
GET    /api/v1/orders          — List scraped orders
GET    /api/v1/orders/{id}     — Get order detail
POST   /api/v1/scraper/trigger  — Manually trigger scraper
GET    /api/v1/scraper/status   — Scraper health
```
Communications (AIPOT-COMMUNICATOR)
```
POST   /api/v1/communications/send  — Send WhatsApp/SMS/Email
GET    /api/v1/communications        — Message history
POST   /api/v1/communications/webhook — Provider webhook receiver
PUT    /api/v1/reminders/preferences  — Notification preferences
```
Billing (AIPOT-BILLING)
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
Research (AIPOT-RESEARCH)
```
POST   /api/v1/research/search  — Semantic search
GET    /api/v1/research/history  — Past searches
GET    /api/v1/research/precedents — Saved precedents
```
Translation (AIPOT-TRANSLATE)
```
POST   /api/v1/translate         — Translate document
GET    /api/v1/translate/{id}   — Check status + download
GET    /api/v1/translate/languages — Supported language pairs
```
Admin (Super Admin only)
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
Scalability Architecture — How to Handle Growth
Current capacity vs future needs
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
Horizontal Scaling Strategy
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
File Structure (Complete Backend)
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
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART 5: AIPOT Agents Deep Dive
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LETESE — 8 AIPOT Agents Deep Dive
> AI Process & Operations Technology
AIPOT-SCRAPER 🔴 HIGH PRIORITY
**Monitor court portals 24/7, detect new orders**
Purpose
Automatically scrape court portals for new orders and case updates. Notify advocates immediately when something new appears.
Courts to Cover (Priority Order)
| Court | URL | CNR Format | Difficulty |
|-------|-----|-----------|------------|
| Supreme Court of India | main.sci.gov.in | SC-YYYY-NNNN | MEDIUM |
| Punjab & Haryana HC | phhc.gov.in | CRM-M-YYYY-NNNNN | MEDIUM |
| Delhi High Court | delhihighcourt.nic.in | WPD-MC-YYYY-NNNNN | MEDIUM |
| NCDRC | ncdrc.nic.in | Consumer Petition | HARD (CAPTCHA) |
| Bombay High Court | bombayhighcourt.nic.in | WP-L-YYYY-NNNNN | MEDIUM |
| All 25 High Courts | individual | Varies | HARD |
Tech Stack
- **Scraping:** Playwright (headless browser) for JavaScript-rendered portals
- **Queue:** Kafka (`letese.scraper.jobs`)
- **Proxy:** Rotating proxy for rate limiting compliance
- **Dedup:** SHA256 hash of order text stored in `court_orders.order_hash`
Flow
```
Kafka topic: letese.scraper.jobs
     │
     ├── [Timer: Every 15 min]
     │       │
     │       ▼
     │   Playwright scraper runs
     │       │
     │       ├── [New orders found?]
     │       │    YES → Save to court_orders table
     │       │         → Kafka: letese.scraper.orders
     │       │         → Match CNR to existing cases
     │       │         → Notify advocate via AIPOT-COMMUNICATOR
     │       │    NO  → Log: "No new orders"
     │       │
     │       └── Kafka: scraper.job.done event
```
CNR Format Examples
```
SC-2025-1234           → Supreme Court
CRM-M-2025-12345       → P&H HC
WPD-MC-2025-1234       → Delhi HC
WP-L-2025-12345        → Bombay HC
```
AIPOT-DRAFT 🔴 HIGH PRIORITY
**AI petition drafting using Qwen3-VL-8B**
Purpose
Generate legal petitions in minutes instead of hours. Advocate enters case details → AI produces formatted draft.
Supported Petition Types
| Petition | Court | Format |
|----------|-------|--------|
| CWP (Civil Writ Petition) | P&H HC | Standard writ format |
| CRM (Criminal Misc.) | P&H HC | Criminal format |
| CRP (Civil Revisional) | P&H HC | Revisional format |
| Writ Petition | Delhi HC | Article 226 format |
| CS (Civil Suit) | Delhi HC | Civil suit format |
| SLP (Special Leave) | Supreme Court | SLP format |
| Consumer Complaint | NCDRC | Consumer protection format |
Tech Stack
- **Model:** AI24x7 Qwen3-VL-8B at `43.242.224.231:8080`
- **Pipeline:** LangChain for prompt templating
- **Document:** python-docx for .docx output, WeasyPrint for PDF
Prompt Template
```
System: You are an expert Indian lawyer drafting {petition_type} for {court_name}.
Format: Strict {format_type} format as per {court} rules.
Language: {language} (English/Hindi/Both)
Instructions: {specific_instructions}
Case Details:
- Client: {client_name}
- Opposing Party: {opposing_party}
- Subject: {case_subject}
- Facts: {facts}
- Relief Sought: {relief}
Generate the complete petition draft.
```
Flow
```
Advocate clicks "Generate Draft"
         │
         ▼
POST /drafts → FastAPI
         │
         ▼
Celery task: generate_draft
         │
         ├── LangChain prompt assembly
         ├── Call AI24x7 Qwen3-VL API
         ├── Format response as petition
         ├── Save to drafts table
         │
         ├── [Auto-trigger AIPOT-COMPLIANCE]
         │         │
         │         ▼
         │   Run compliance checks
         │         │
         │         ▼
         │   Save suggestions to ai_suggestions
         │
         ▼
Return draft to advocate
         │
         ├── Advocate reviews
         ├── Edits if needed
         └── Clicks "Approve" → status: approved
                   │
                   ▼
             File in court
```
AIPOT-COMPLIANCE 🔴 HIGH PRIORITY
**Validate drafts against court checklists**
Purpose
Catch errors before filing. Run automated checks on AI-generated drafts.
Check Types
| Check | What it validates |
|-------|------------------|
| Format Check | Page limits, font size (12pt), margins (1 inch) |
| Document Check | Vakalatnama, affidavit, index attached |
| Fee Check | Court fee stamp duty paid |
| CNR Check | Correct CNR number format |
| Party Check | All parties named correctly in cause list |
| Timeline Check | Within limitation period (Article 137, etc.) |
| Language Check | Hindi/English compliance |
Compliance Report (JSONB saved)
```json
{
  "score": 85.5,
  "checks": [
    {"type": "format", "status": "pass", "detail": "Font 12pt ✓"},
    {"type": "fee", "status": "warning", "detail": "Court fee ₹50 found, expected ₹500"},
    {"type": "timeline", "status": "pass", "detail": "Within 90-day period ✓"},
    {"type": "party", "status": "error", "detail": "Respondent name missing in para 3"}
  ],
  "suggestions": [
    {"line": "para 3", "fix": "Add respondent full name with address"}
  ]
}
```
AIPOT-COMMUNICATOR 🔴 HIGH PRIORITY
**Send reminders via WhatsApp/SMS/Email/Voice**
Purpose
Auto-remind clients and advocates about hearings at 15 days, 7 days, 48 hours, and 24 hours before.
Channels
| Channel | Provider | Use Case |
|---------|----------|----------|
| WhatsApp | 360dialog BSP | Primary — rich messages, templates |
| SMS | MSG91 | Fallback / urgent alerts |
| Email | SendGrid | Invoices, formal notices |
| Voice | AI24x7 TTS | Hearing reminders (AI calls) |
Reminder Schedule
```
Case hearing: March 15, 2026 at 10:00 AM
15 days before  → WhatsApp: "Reminder: Hearing on Mar 15 in CNR XYZ"
7 days before   → WhatsApp + SMS: "Urgent: Hearing in 1 week"
48 hours before → WhatsApp + SMS + Email
24 hours before → WhatsApp + SMS + Voice call (AI)
```
Message Templates (WhatsApp)
```
15_day: "🗓️ *Reminder:* Hearing on {date} at {time} in {court}. Case: {case_no}. - LETESE"
7_day: "⚠️ *Urgent:* Hearing in 7 days — {date}, {time} at {court}. Case: {case_no}. Prepare all documents. - LETESE"
48_hour: "🚨 *48 hours:* Hearing tomorrow at {time}. Court: {court}. Case: {case_no}. - LETESE"
24_hour: "📞 *AI Call:* Your hearing is tomorrow at {time}. Please confirm availability. - LETESE"
```
AIPOT-POLICE 🟡 MEDIUM
**System health monitoring**
Purpose
Ensure all systems are running. Alert if something breaks.
Checks (every 10 min / 60 min)
| Check | What | Alert if |
|-------|------|----------|
| API Health | GET /health | Response > 500ms or 5xx |
| Database | SELECT 1 | Connection fails |
| Redis | PING | Not responding |
| Kafka | Consumer lag | > 1000 messages pending |
| AI Server | GET /v1/models | Model not loaded |
| S3 Storage | List buckets | Access denied |
| Scraper | Last successful scrape | > 2 hours ago |
Alerts
- Minor: Slack/Discord webhook
- Major: SMS to Arjun + Email
AIPOT-BILLING 🟡 MEDIUM
**Automated invoices + GST + Razorpay**
Purpose
Generate GST-compliant invoices automatically. Handle subscription billing.
Invoice Format (per GST rules)
```
LETESE.INV-2026-00001
From:
GOUP Consultancy Services LLP
[Address]
To:
[Advocate Name]
[Address]
Description          Qty    Rate      Amount
─────────────────────────────────────────────
Professional Plan      1    ₹4,999    ₹4,999
                                  ────────────
Subtotal:                         ₹4,999.00
GST (18%):                          ₹899.82
                                  ════════════
TOTAL:                            ₹5,898.82
Payment Link: https://razorpay.in/pay/...
Due Date: 7 days
```
Flow
```
Plan upgrade / Invoice request
         │
         ▼
POST /invoices → FastAPI
         │
         ▼
AIPOT-BILLING:
  ├── Generate invoice_no: LETESE-INV-2026-NNNNN
  ├── Calculate GST (18%)
  ├── Create PDF with WeasyPrint
  ├── Save to S3
  ├── Create Razorpay order
  │
  ▼
Send invoice via Email + WhatsApp
         │
         ▼
Advocate pays via Razorpay
         │
         ▼
Razorpay webhook → Payment confirmed
         │
         ▼
Update subscription status
Send confirmation via WhatsApp
```
AIPOT-RESEARCH 🟢 LOW
**Legal precedent search using pgvector**
Purpose
Semantic search across all court orders, judgments, and legal documents. Find similar cases or relevant precedents.
Tech Stack
- **pgvector:** Vector embeddings stored in `vector_cache` table
- **Embedding model:** Sentence-transformers (`all-MiniLM-L6-v2`)
- **Search:** Cosine similarity on vector column
Flow
```
Advocate searches: "bail under section 437 crpc"
         │
         ▼
GET /research?q=...
         │
         ▼
AIPOT-RESEARCH:
  ├── Generate query embedding
  ├── Cosine similarity search on vector_cache
  ├── Top 10 results
  ├── Return with case citations
         │
         ▼
Display: Case list with relevance scores + excerpts
```
AIPOT-TRANSLATE 🟡 MEDIUM
**Multilingual legal translation EN/HI/PA**
Purpose
Translate legal documents between English, Hindi, and Punjabi with high accuracy.
Tech Stack
- **Model:** AI24x7 Meta MMS fine-tuned (or AI4Bharat IndicWav2Vec)
- **Output:** Preserved formatting (PDF/DOCX)
Supported Languages
- English (en)
- Hindi (hi)
- Punjabi (pa)
Accuracy Target
- Technical legal terms: 95%+ accuracy
- General content: 90%+ accuracy
- Confidence score stored in `translation_jobs.accuracy_score`
Summary Table
| Agent | Trigger | Output | Priority |
|-------|---------|--------|----------|
| AIPOT-SCRAPER | Every 15 min (Kafka) | court_orders table | 🔴 HIGH |
| AIPOT-DRAFT | Advocate clicks "Generate" | drafts table + file | 🔴 HIGH |
| AIPOT-COMPLIANCE | After draft generated | ai_suggestions table | 🔴 HIGH |
| AIPOT-COMMUNICATOR | Hearing dates (15d/7d/48h/24h) | communications table | 🔴 HIGH |
| AIPOT-POLICE | Every 10/60 min (cron) | Slack/SMS alerts | 🟡 MEDIUM |
| AIPOT-BILLING | Invoice request / payment | invoices table + PDF | 🟡 MEDIUM |
| AIPOT-RESEARCH | Advocate searches | Court orders ranked | 🟢 LOW |
| AIPOT-TRANSLATE | Document upload | Translated file | 🟡 MEDIUM |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART 4: FastAPI Backend Structure
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LETESE — FastAPI Backend Structure (File-by-File)
Overview
**Stack:** Python 3.11+ | FastAPI | SQLAlchemy 2.0 (async) | PostgreSQL + pgvector | Redis | Kafka | Celery
**Location:** Server 43.242.224.231
**Port:** 4007 (must replace ZUMMP API)
Project Structure
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
Key API Routes
Auth: `/api/v1/auth`
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
Advocates: `/api/v1/advocates`
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
Cases: `/api/v1/cases`
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
Drafts (AI): `/api/v1/drafts`
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
Court Orders: `/api/v1/court-orders`
```
GET  /court-orders         # List (filterable by case, court, date)
GET  /court-orders/{id}    # Order detail
GET  /court-orders/{id}/summary  # AI summary
POST /court-orders/scrape   # Trigger manual scrape (AIPOT-SCRAPER)
GET  /courts                # List supported courts
```
Documents: `/api/v1/documents`
```
POST /documents/upload     # Upload document (multipart)
GET  /documents/{id}       # Document detail
GET  /documents/{id}/download  # Presigned download URL
PUT  /documents/{id}       # Update metadata
DELETE /documents/{id}     # Soft delete
POST /documents/{id}/verify # Mark verified (admin)
```
Payments: `/api/v1/payments`
```
POST /payments/initiate    # Create Razorpay order
POST /payments/confirm     # Confirm payment
POST /payments/webhook     # Razorpay webhook
GET  /payments/{id}
GET  /payments/history
```
Reminders: `/api/v1/reminders`
```
GET  /reminders            # My scheduled reminders
POST /reminders            # Create reminder
PUT  /reminders/{id}       # Update
DELETE /reminders/{id}     # Cancel
GET  /reminders/upcoming   # Next 7 days
```
Admin: `/api/v1/admin`
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
Multi-Tenant Setup (Critical)
```python
# app/core/tenant.py
from contextvars import ContextVar
tenant_id: ContextVar[UUID | None] = ContextVar("tenant_id", default=None)
In FastAPI middleware (app/main.py):
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    if token := request.headers.get("Authorization"):
        payload = decode_jwt(token.replace("Bearer ", ""))
        tenant_id.set(payload.get("tenant_id"))
    response = await call_next(request)
    return response
Usage in any query:
def get_cases(db: AsyncSession, tenant_id: UUID):
    result = await db.execute(
        select(Case).where(Case.tenant_id == tenant_id)  # RLS enforced
    )
```
Kafka Topics
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
Environment Variables
```env
# App
APP_ENV=development
SECRET_KEY=<32-char-random>
FRONTEND_URL=https://app.letese.xyz
Database (existing)
DATABASE_URL=postgresql+asyncpg://postgres:password@187.127.139.147:5433/ai_drafting
REDIS_URL=redis://187.127.139.147:6379/0
Kafka
KAFKA_BOOTSTRAP_SERVERS=43.242.224.231:9092
AI Server (existing)
AI24X7_API_URL=http://43.242.224.231:8080
AI24X7_API_KEY=<key-if-required>
Razorpay
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=
WhatsApp (360dialog)
W360_API_KEY=
W360_WABA_ID=
SMS (MSG91)
MSG91_AUTH_KEY=
MSG91_SENDER_ID=LETESE
Email (SendGrid)
SENDGRID_API_KEY=
FROM_EMAIL=noreply@letese.co
File Storage (Local S3-like)
STORAGE_BASE_PATH=/data/letese-docs
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART 3: 60-Day Build Plan
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LETESE — 60-Day Build Plan
## Starting: 27 April 2026
PHASE 1: FOUNDATION (Days 1–15)
Week 1
| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 1 | Build LETESE FastAPI backend — Auth (Register/Login/JWT/OTP) | 8 | 🔴 HIGH |
| 2 | Build Advocates CRUD + Profile API | 4 | 🔴 HIGH |
| 3 | Build Cases CRUD API | 5 | 🔴 HIGH |
| 4 | Fix Super Admin Dashboard — replace ZUMMP data + branding | 10 | 🔴 HIGH |
| 5 | Connect Customer Dashboard to new LETESE API | 8 | 🔴 HIGH |
| 6 | Align database pricing (₹4,999 / ₹10,999) with website | 2 | 🔴 HIGH |
Week 2
| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 7 | Install Kafka on server 43.242.224.231 | 3 | 🟡 MEDIUM |
| 8 | Build AIPOT-SCRAPER — P&H HC + Delhi HC | 15 | 🔴 HIGH |
| 9 | Build AIPOT-DRAFT — connect AI24x7 Qwen3-VL | 10 | 🔴 HIGH |
| 10 | Build AIPOT-COMPLIANCE — checklist validation engine | 10 | 🔴 HIGH |
| 11 | Build Clients CRUD API | 3 | 🟡 MEDIUM |
| 12 | Build Documents upload/download API (S3) | 4 | 🟡 MEDIUM |
Week 3
| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 13 | Build AIPOT-COMMUNICATOR — reminder scheduling | 12 | 🔴 HIGH |
| 14 | Connect 360dialog WhatsApp Business API | 8 | 🔴 HIGH |
| 15 | Razorpay payment integration + GST invoices | 10 | 🔴 HIGH |
| 16 | RBAC — Team roles + permissions (6 roles) | 6 | 🟡 MEDIUM |
| 17 | Build Drafts API + AI draft storage | 4 | 🟡 MEDIUM |
PHASE 2: ADVANCED FEATURES (Days 16–35)
Week 4
| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 18 | AIPOT-POLICE — System health monitoring (cron) | 8 | 🟡 MEDIUM |
| 19 | AIPOT-RESEARCH — pgvector legal precedent search | 12 | 🟡 MEDIUM |
| 20 | AIPOT-TRANSLATE — EN/HI/PA translation (Meta MMS) | 8 | 🟡 MEDIUM |
| 21 | Client-facing branded portal (white-label subdomain) | 10 | 🟡 MEDIUM |
| 22 | Build Invoices API + WeasyPrint PDF generation | 5 | 🟡 MEDIUM |
| 23 | Build Subscriptions API + plan management | 4 | 🟡 MEDIUM |
Week 5
| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 24 | Court scraper — Supreme Court + NCDRC | 15 | 🟡 MEDIUM |
| 25 | Calendar + hearing date management UI | 8 | 🟡 MEDIUM |
| 26 | Migrate all LETESE services to server 43.242.224.231 | 6 | 🟡 MEDIUM |
| 27 | Document version history + audit trail | 5 | 🟡 MEDIUM |
| 28 | Court orders API + AI summary generation | 5 | 🟡 MEDIUM |
| 29 | Build Tasks API (to-do items) | 4 | 🟡 MEDIUM |
Week 6
| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 30 | AIPOT-BILLING — Automated invoice + GST generation | 10 | 🟡 MEDIUM |
| 31 | Full testing + bug fixing | 15 | 🟡 MEDIUM |
| 32 | Performance optimization (query tuning, caching) | 5 | 🟡 MEDIUM |
| 33 | API rate limiting + security hardening | 4 | 🟡 MEDIUM |
| 34 | WebSocket for real-time notifications | 5 | 🟡 MEDIUM |
PHASE 3: MOBILE + DEPLOY (Days 36–60)
Week 7
| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 35 | Flutter Web build setup | 8 | 🟢 LOW |
| 36 | Flutter Android + iOS build | 12 | 🟢 LOW |
| 37 | Mobile — Login + Dashboard screens | 8 | 🟢 LOW |
| 38 | Mobile — Case list + Case detail screens | 8 | 🟢 LOW |
| 39 | Mobile — Document viewer + uploader | 6 | 🟢 LOW |
Week 8
| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 40 | Mobile — AI Draft generation screen | 8 | 🟢 LOW |
| 41 | Mobile — Translation screen | 7 | 🟢 LOW |
| 42 | Mobile — Client management | 5 | 🟢 LOW |
| 43 | Deploy to production (letese.xyz, app.letese.xyz, admin.letese.xyz) | 10 | 🟢 LOW |
| 44 | SSL certificates + CDN + domain setup | 5 | 🟢 LOW |
| 45 | CI/CD pipeline (GitHub Actions) | 5 | 🟢 LOW |
Week 9
| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 46 | User acceptance testing (UAT) with real advocates | 15 | 🟢 LOW |
| 47 | Bug fixes + final polish | 15 | 🟢 LOW |
| 48 | Documentation + API docs (Swagger/OpenAPI) | 5 | 🟢 LOW |
| 49 | Launch checklist + monitoring setup | 5 | 🟢 LOW |
IMMEDIATE ACTIONS (This Week)
| # | Task | Decision Needed |
|---|------|----------------|
| A | Confirm: Server 43.242.224.231 to host LETESE backend? | YES/NO |
| B | Confirm: Use AI24x7 Qwen3-VL for AIPOT-DRAFT (saves API cost)? | YES/NO |
| C | Confirm: WhatsApp Business — do you have 360dialog account? | YES/NO |
| D | Confirm: Razorpay account ready for LIVE payments? | YES/NO |
| E | Confirm: Flutter for mobile app (web + Android + iOS)? | YES/NO |
| F | Who is the REAL Super Admin? Only Arjun or team too? | Clarify |
| G | What are the FIRST 3 courts to scrape? | P&H HC priority |
Estimated Monthly Running Cost
| Resource | Cost |
|----------|------|
| Server 43.242.224.231 | ₹0 (already paid) |
| GPU (AI Drafting) | ₹0 (your GPU) |
| Kafka + Redis (local) | ₹0 |
| 360dialog WhatsApp | ₹5,000–15,000/mo |
| MSG91 SMS | ₹2,000–5,000/mo |
| Razorpay (2% fee) | Variable |
| Domain + SSL | ₹1,000/yr |
| **TOTAL** | **₹8,000–20,000/mo** |
**vs Competition:** ₹20,000+/mo — LETESE is 50–60% cheaper!
LETESE — Realistic Timeline, Architecture & Complete Project Plan
> Deep Planning Document | Date: 27 April 2026 | Version: 1.0
Executive Summary
**Total Time for Full v1.0:** 90 Days (Realistic)  
**Minimum Viable Product (MVP):** 45 Days  
**Team假设:** 1 developer (Arjun) + AI assistant (me)
> ⚠️ 60-day plan mentioned earlier was optimistic. Real engineering needs 90 days for production-quality system that handles billions of records smoothly.
The Big Picture — What We're Building
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
Architecture for Billions of Records (Scale)
Problem: Most SaaS crashes when data grows
- 1 firm = 10,000 cases
- 100 firms = 1,000,000 cases
- 10,000 firms = 100,000,000 cases
**Solution: Sharding + Partitioning + Smart Caching**
Database Strategy (PostgreSQL at scale)
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
AI Server Strategy (Handle millions of AI calls)
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
Caching Strategy (Redis)
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
File Storage Strategy (S3 / Local)
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
Complete System Architecture Diagram
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
The 8 AIPOT Agents — Technical Design
How They Work Together
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
Realistic Timeline — 90 Days (12 Weeks)
Phase 0 — Foundation Setup (Days 1-7)
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
| 7 | **Milestone:** Auth + DB ready, can create tenant + user Phase 1A — Core Backend (Days 8-21)
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
Phase 1B — Frontend MVP (Days 15-30) [PARALLEL]
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
Phase 2 — 4 AIPOT Agents + Integrations (Days 22-50)
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
Phase 3 — Billing + Research + Translate (Days 51-65)
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
Phase 4 — Super Admin + Client Portal (Days 66-78)
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
Phase 5 — Hardening + Launch (Days 79-90)
| Day | Task | Deliverable |
|-----|------|-------------|
| 79-81 | Load testing | k6 scripts, 1000 concurrent users |
| 81-83 | Security audit | SQL injection, XSS, RBAC bypass tests |
| 83-85 | Performance optimization | DB indexes, Redis cache, query优化 |
| 85-87 | Documentation | API docs (Swagger), admin guide, user guide |
| 87-89 | Deployment | Docker compose, CI/CD pipeline, monitoring |
| 90 | **LAUNCH DAY** | v1.0 live at letese.xyz |
Critical Path — What to Build in What Order
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
Database Design for Scale (25 Tables)
Core Tables
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
API Design — All Endpoints
Authentication
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
Cases
```
GET    /api/v1/cases            — List cases (paginated, filtered)
POST   /api/v1/cases            — Create case
GET    /api/v1/cases/{id}       — Get case detail
PUT    /api/v1/cases/{id}       — Update case
DELETE /api/v1/cases/{id}       — Soft delete case
GET    /api/v1/cases/{id}/timeline — Case history
POST   /api/v1/cases/{id}/parties  — Add party to case
```
Hearings
```
GET    /api/v1/hearings         — List hearings
POST   /api/v1/hearings         — Create hearing
GET    /api/v1/hearings/{id}    — Get hearing
PUT    /api/v1/hearings/{id}    — Update hearing
DELETE /api/v1/hearings/{id}    — Delete hearing
GET    /api/v1/hearings/upcoming — Hearings in next 7 days
```
Documents
```
POST   /api/v1/documents/upload — Upload file (multipart)
GET    /api/v1/documents/{id}   — Download file (presigned URL)
DELETE /api/v1/documents/{id}   — Delete file
GET    /api/v1/documents        — List documents (filtered by case)
```
AI Drafts (AIPOT-DRAFT)
```
POST   /api/v1/drafts/generate  — Generate AI petition
GET    /api/v1/drafts           — List drafts
GET    /api/v1/drafts/{id}      — Get draft + compliance report
PUT    /api/v1/drafts/{id}      — Edit draft
POST   /api/v1/drafts/{id}/approve — Approve draft
POST   /api/v1/drafts/{id}/reject  — Reject draft
GET    /api/v1/drafts/templates — List petition templates
```
Court Orders (AIPOT-SCRAPER)
```
GET    /api/v1/courts           — List supported courts
GET    /api/v1/orders          — List scraped orders
GET    /api/v1/orders/{id}     — Get order detail
POST   /api/v1/scraper/trigger  — Manually trigger scraper
GET    /api/v1/scraper/status   — Scraper health
```
Communications (AIPOT-COMMUNICATOR)
```
POST   /api/v1/communications/send  — Send WhatsApp/SMS/Email
GET    /api/v1/communications        — Message history
POST   /api/v1/communications/webhook — Provider webhook receiver
PUT    /api/v1/reminders/preferences  — Notification preferences
```
Billing (AIPOT-BILLING)
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
Research (AIPOT-RESEARCH)
```
POST   /api/v1/research/search  — Semantic search
GET    /api/v1/research/history  — Past searches
GET    /api/v1/research/precedents — Saved precedents
```
Translation (AIPOT-TRANSLATE)
```
POST   /api/v1/translate         — Translate document
GET    /api/v1/translate/{id}   — Check status + download
GET    /api/v1/translate/languages — Supported language pairs
```
Admin (Super Admin only)
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
Scalability Architecture — How to Handle Growth
Current capacity vs future needs
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
Horizontal Scaling Strategy
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
File Structure (Complete Backend)
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
| ✅ |
━━━━━━━━━━━━━━ PART 2: Architecture & Timeline ━━━━━━━━━━━━━━
LETESE — Complete Project Documentation
> Version 1.0 | Date: 27 April 2026 | Owner: Arjun Singh | Company: GOUP Consultancy Services LLP
📋 Table of Content
1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Our Solution](#3-our-solution)
4. [8 AIPOT Agents](#4-eight-aipot-agents)
5. [Tech Stack](#5-tech-stack)
6. [Database Schema](#6-database-schema)
7. [User Roles & Access](#7-user-roles--access)
8. [Multi-Tenant SaaS Architecture](#8-multi-tenant-saas-architecture)
9. [Pricing Plans](#9-pricing-plans)
10. [Brand Guidelines](#10-brand-guidelines)
11. [60-Day Build Plan](#11-60-day-build-plan)
12. [FastAPI Backend Structure](#12-fastapi-backend-structure)
13. [AIPOT Agents Deep Dive](#13-aipot-agents-deep-dive)
14. [Critical Issues to Fix](#14-critical-issues-to-fix)
15. [Entry Flow (How a New Advocate Joins)](#15-entry-flow-new-advocate-joins)
16. [Server Resources](#16-server-resources)
17. [Competitor Analysis](#17-competitor-analysis)
18. [Running Cost](#18-running-cost)
1. Project Overview
What is LETESE?
**LETESE** = **LE**gal **TE**ch **SE**rvices  
An AI-powered Legal Practice Management SaaS platform for Indian advocates, law firms, and legal professionals.
**What it does:** Automates case management, court monitoring, AI drafting, billing, and client communications — all in one platform.
| URL | Purpose | Status |
|-----|---------|--------|
| https://letese.xyz | Landing page (React SPA) | ✅ Live |
| https://app.letese.xyz | Customer dashboard | ⚠️ No backend |
| https://admin.letese.xyz | Super Admin portal | ⚠️ Shows wrong data |
**Company:** GOUP Consultancy Services LLP  
**Platform Type:** Multi-tenant SaaS (one database, many law firms)  
**Target Market:** Indian advocates, law firms, legal departments  
**Geographic Focus:** India (all 25 High Courts + Supreme Court)
2. Problem Statement
Pain Points for Indian Advocates
| Problem | Impact |
|---------|--------|
| Manual case tracking (Excel/physical diary) | Cases missed, clients unhappy |
| No court order monitoring | Important orders missed |
| Hours spent drafting petitions | Billable time lost |
| Client reminder failures | Court appearances missed |
| Manual invoicing | Cash flow problems |
| Language barriers (HI/PA/EN) | Communication gaps |
| High software costs (₹20,000+/month) | Unaffordable for small firms |
Current Market Gap
- Existing tools: Complex, expensive, not AI-native
- Cuto, Legistify, Lawrato: Generic, no court integration
- No tool has: AI drafting + court scraper + multi-language + affordable pricing
- **LETESE fills this gap** with 8 AI agents + ₹4,999/month pricing
3. Our Solution
LETESE vs Traditional Practice Management
| Feature | Traditional | LETESE |
|---------|-------------|--------|
| Case Tracking | Manual Excel | Automated dashboard |
| Court Orders | Manual checking | AI scraper 24/7 |
| Petition Drafting | 4-8 hours | 5 minutes (AI) |
| Client Reminders | Manual calls/SMS | Auto WhatsApp/SMS/Email/Voice |
| Invoicing | Manual GST invoicing | Auto Razorpay + GST |
| Translation | Expensive translator | AI (EN/HI/PA) |
| Legal Research | Hours of reading | 30-second semantic search |
| Monthly Cost | ₹20,000+ | ₹4,999/month |
Competitive Advantage
- **AI24x7 Qwen3-VL-8B** runs on our own GPU server = ₹0 AI cost
- Competitors pay ₹0.50/1000 tokens to OpenAI
- We can pass savings to users = lower pricing
- All AI processing happens in India (data sovereignty)
4. Eight AIPOT Agents
> AIPOT = **AI Process & Operations Technology**  
> Each agent is an autonomous AI worker that performs one specific job 24/7.
| # | Agent | What it does | Priority |
|---|-------|-------------|----------|
| 1 | **AIPOT-SCRAPER** | Monitor court portals 24/7, detect new orders, notify advocates | 🔴 HIGH |
| 2 | **AIPOT-DRAFT** | AI petition drafting using Qwen3-VL-8B (5-minute drafts) | 🔴 HIGH |
| 3 | **AIPOT-COMPLIANCE** | Validate drafts against court checklists, catch errors before filing | 🔴 HIGH |
| 4 | **AIPOT-COMMUNICATOR** | Send WhatsApp/SMS/Email/Voice reminders at 15d/7d/48h/24h | 🔴 HIGH |
| 5 | **AIPOT-POLICE** | Monitor all system health, alert if something breaks | 🟡 MEDIUM |
| 6 | **AIPOT-BILLING** | Auto GST invoices via Razorpay, subscription management | 🟡 MEDIUM |
| 7 | **AIPOT-RESEARCH** | Semantic legal research across all court orders (pgvector) | 🟢 LOW |
| 8 | **AIPOT-TRANSLATE** | Multilingual legal translation EN/HI/PA (Meta MMS) | 🟡 ME5. Tech Stack
Frontend
| Layer | Technology | Notes |
|-------|-----------|-------|
| Marketing Website | React SPA | Hosted at 187.127.139.147:4009 |
| Customer App | Flutter Web + Mobile | To be built |
| Admin Dashboard | React | admin.letese.xyz |
| Design System | Glassmorphism 2.0 | Dark theme, glass cards |
Backend
| Layer | Technology | Location |
|-------|-----------|----------|
| API Server | Python FastAPI | 43.242.224.231 (ports TBD) |
| Database | PostgreSQL + pgvector | 187.127.139.147:5433 |
| Real-time DB | MongoDB | 187.127.139.147:27018 |
| Cache | Redis | 187.127.139.147:6379 |
| Message Queue | Kafka | 43.242.224.231 |
| AI Server | Qwen3-VL-8B (AI24x7) | 43.242.224.231:8080 |
| File Storage | S3 / Local Disk | 43.242.224.231 |
| Scheduler | Celery + Redis | Background task runner |
External Integrations
| Service | Provider | Purpose |
|---------|----------|---------|
| WhatsApp | 360dialog BSP | Client communications |
| SMS | MSG91 | Fallback alerts |
| Email | SendGrid | Formal notices, invoices |
| Payments | Razorpay | Subscription billing |
| Voice | ElevenLabs / AI24x7 TTS | AI voice calls |
| AI | AI24x7 Qwen3-VL | Drafting + Research + Translation |
Court Portals (AIPOT-SCRAPER targets)
| Court | URL | Priority |
|-------|-----|----------|
| Supreme Court of India | main.sci.gov.in | 🔴 HIGH |
| Punjab & Haryana HC | phhc.gov.in | 🔴 HIGH |
| Delhi High Court | delhihighcourt.nic.in | 🔴 HIGH |
| NCDRC | ncdrc.nic.in | 🟡 MEDIUM |
| Bombay High Court | bombayhighcourt.nic.in | 🟡 MEDIUM |
| All other 20 HCs | individual portals | 🟢 L
6. Database Schema (25 Tables)
PostgreSQL database with Row-Level Security (RLS) for multi-tenant isolation.
> Full schema: `letese/docs/02-database-schema.md`
Key tables:
- `tenants` — Law firm/advocate account
- `users` — Team members (advocate, clerk, paralegal, intern)
- `roles` — RBAC permissions
- `cases` — All case records
- `case_parties` — Plaintiff, defendant, advocate links
- `hearings` — Hearing schedule with reminders
- `documents` — Uploaded files (S3 links)
- `drafts` — AI-generated petitions
- `court_orders` — Scraped court orders
- `communications` — WhatsApp/SMS/Email/Voice logs
- `invoices` — GST invoices
- `subscriptions` — Plan management
- `vector_cache` — pgvector embeddings for research
- `ai_suggestions` — Compliance check results
- `translation_jobs` — Translation job tracking
7. User Roles & Access
| Role | Who | Access | Dashboard |
|------|-----|--------|-----------|
| **Super Admin** | LETESE Team (Arjun) | Full system, all tenants, billing, config | admin.letese.xyz |
| **Advocate Admin** | Law Firm Owner | Full access to own firm | app.letese.xyz |
| **Advocate** | Senior Advocate | Own cases, all features | app.letese.xyz |
| **Clerk** | Court Clerk | Create/view cases, upload docs | app.letese.xyz |
| **Paralegal** | Junior Lawyer | Clerk + trigger communications | app.letese.xyz |
| **Intern** | Law Student | View assigned cases only | app.letese.xyz |
| **Client** | End Client | Own case status, documents, reminders | Branded portal (subdomain) |
Client White-Label Portal
- Each law firm gets a branded portal: `firmname.letese.xyz`
- Clients see only their own cases
- No access to firm data or other clients
- Full mobile responsiveness
8. Multi-Tenant SaaS Architecture
**Concept:** ONE PostgreSQL database, ONE schema, MULTIPLE tenants (law firms)
```
PostgreSQL Database (187.127.139.147:5433)
├── tenant_id = "firm_uuid_1" → Law Firm A's data
├── tenant_id = "firm_uuid_2" → Law Firm B's data
└── tenant_id = "firm_uuid_3" → Law Firm C's data
All queries filtered by tenant_id from JWT token
Row-Level Security (RLS) enforces isolation at DB level
```
Isolation Strategy
| Resource | Strategy |
|---------|----------|
| PostgreSQL | RLS (Row-Level Security) on all tables |
| S3 Storage | One folder per tenant: `s3://letese-docs/tenant_uuid/` |
| Redis | Keys prefixed: `session:tenant_uuid:user_id` |
| Kafka | Topics namespaced: `letese.{tenant_id}.scraper.jobs` |
| AI Processing | Tenant context passed in every API call |
9. Pricing Plans (CORRECT — per website)
> ⚠️ Database currently has wrong pricing (₹999/₹2,999). Must update.
| Plan | Monthly | Annual | Cases | Storage | Features |
|------|---------|--------|-------|---------|---------|
| **Basic** | FREE | — | 30 | 5 GB | Email reminders, case tracking |
| **Professional** | ₹4,999 | ₹3,999/mo | 200 | 50 GB | SMS + WhatsApp, billing, 3 seats |
| **Elite** | ₹10,999 | ₹8,999/mo | 500 | 200 GB | AI drafting, HC/SC checklist, translation, voice |
| **Enterprise** | Custom | — | Unlimited | Unlimited | All AIPOTs, API access, white-label, dedicated manager |
Plan Upgrade Flow
1. User signs up → Basic (FREE) plan
2. User clicks "Upgrade" → Razorpay payment page
3. Payment success → Subscription activated
4. All features of plan unlocked instantly
10. Brand Guidelines
Colors (Glassmorphism 2.0)
| Color | Hex | Usage |
|-------|-----|-------|
| Brand Blue | `#1A4FBF` | Logo, primary buttons, header |
| Brand Green | `#22C55E` | Logo dot ●, success states, CTAs |
| Neon Cyan | `#00D4FF` | Interactive highlights, links |
| Electric Purple | `#8B5CF6` | AI elements, premium features |
| Page Background | `#0A0E1A` | Deep space background |
| Glass Card | `rgba(255,255,255,0.05)` | All cards with backdrop blur |
| Text Primary | `#F0F4FF` | Main text |
| Text Secondary | `#8899BB` | Secondary labels |
Typography
- Headings: Inter / Poppins
- Body: Inter
- Monospace (code): JetBrains Mono
Logo Concept
```
[LETESE] — Legal Tech Services
 ● (green dot after LETESE text)
```
Design Reference
- Dark glassmorphism theme
- Free template: templatemo.com/tm-607-glass-admin
- Competitor reference: Clio.com (gold standard legal SaaS)
11. 60-Day Build Plan
> Full plan: `letese/docs/03-60-day-build-plan.md`
Phase 1 — Foundation (Days 1-20)
- [ ] Rebuild LETESE FastAPI backend from scratch
- [ ] Fix database pricing, branding, all ZUMMP references
- [ ] Connect PostgreSQL (21 existing tables)
- [ ] User authentication (signup/login/JWT)
- [ ] Case management CRUD
- [ ] Document upload (S3/local)
- [ ] Super Admin dashboard (admin.letese.xyz)
Phase 2 — AI + Communications (Days 21-40)
- [ ] Connect AI24x7 Qwen3-VL at port 8080
- [ ] AIPOT-DRAFT: AI petition generation
- [ ] AIPOT-COMPLIANCE: Draft validation
- [ ] AIPOT-COMMUNICATOR: WhatsApp (360dialog)
- [ ] Reminder system (15d/7d/48h/24h)
- [ ] Email integration (SendGrid)
- [ ] SMS integration (MSG91)
Phase 3 — Courts + Billing (Days 41-60)
- [ ] AIPOT-SCRAPER: P&H HC + Delhi HC scraper
- [ ] Kafka queue setup for scraper workers
- [ ] AIPOT-BILLING: Razorpay + GST invoices
- [ ] Subscription management
- [ ] AIPOT-RESEARCH: pgvector semantic search
- [ ] AIPOT-TRANSLATE: EN/HI/PA translation
- [ ] Client white-label portal
- [ ] Flutter mobile app (basic)
12. FastAPI Backend Structure
> Full structure: `letese/docs/04-fastapi-backend-structure.md`
```
letese-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry
│   ├── config.py               # Environment variables
│   ├── database.py             # PostgreSQL connection
│   ├── models/                  # SQLAlchemy models
│   │   ├── tenant.py
│   │   ├── user.py
│   │   ├── case.py
│   │   ├── document.py
│   │   └── ...
│   ├── schemas/                 # Pydantic schemas
│   │   ├── auth.py
│   │   ├── case.py
│   │   └── ...
│   ├── routers/                 # API routes
│   │   ├── auth.py             # /api/auth/*
│   │   ├── cases.py            # /api/cases/*
│   │   ├── drafts.py           # /api/drafts/*
│   │   ├── scraper.py          # /api/scraper/*
│   │   ├── billing.py          # /api/billing/*
│   │   └── ...
│   ├── services/               # Business logic
│   │   ├── ai_service.py       # AI24x7 Qwen3-VL
│   │   ├── whatsapp_service.py # 360dialog
│   │   ├── razorpay_service.py
│   │   └── ...
│   ├── agents/                 # AIPOT agents
│   │   ├── scraper.py
│   │   ├── draft.py
│   │   ├── compliance.py
│   │   ├── communicator.py
│   │   ├── police.py
│   │   ├── billing.py
│   │   ├── research.py
│   │   └── translate.py
│   ├── tasks/                  # Celery tasks
│   │   ├── draft_tasks.py
│   │   ├── scraper_tasks.py
│   │   └── reminder_tasks.py
│   └── middleware/
│       ├── tenantMiddleware.py  # Extract tenant_id from JWT
│       └── rate_limit.py
├── alembic/                    # DB migrations
├── tests/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
Key API Endpoints
```
Authentication:
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh
POST   /api/auth/logout
Cases:
GET    /api/cases
POST   /api/cases
GET    /api/cases/{id}
PUT    /api/cases/{id}
DELETE /api/cases/{id}
Documents:
POST   /api/documents/upload
GET    /api/documents/{id}
DELETE /api/documents/{id}
Drafts (AIPOT-DRAFT):
POST   /api/drafts/generate
GET    /api/drafts
GET    /api/drafts/{id}
POST   /api/drafts/{id}/approve
Scraper (AIPOT-SCRAPER):
GET    /api/scraper/courts
POST   /api/scraper/trigger
GET    /api/scraper/orders
Billing (AIPOT-BILLING):
POST   /api/invoices
GET    /api/invoices
POST   /api/payments/razorpay/webhook
Admin:
GET    /api/admin/tenants
GET    /api/admin/usage
```
13. AIPOT Agents Deep Dive
> Full details: `letese/docs/05-aipot-agents.md`
AIPOT-SCRAPER (Priority: 🔴 HIGH
- Monitors court portals every 15 minutes using Playwright
- Kafka queue: `letese.scraper.jobs`
- CNR format validation (SC-YYYY-NNNN, CRM-M-YYYY-NNNNN, etc.)
- Dedup via SHA256 hash of order text
- On new order → notify advocate via AIPOT-COMMUNICATOR
AIPOT-DRAFT (Priority: 🔴 HIGH
- Advocate enters case details → 5-minute AI draft
- Connected to AI24x7 Qwen3-VL at `43.242.224.231:8080`
- Supported: CWP, CRM, CRP, Writ, CS, SLP, Consumer Complaint
- Output: .docx + .pdf, formatted as per court rules
- Triggers AIPOT-COMPLIANCE after generation
AIPOT-COMPLIANCE (Priority: 🔴 HIGH
- Runs 7 checks on every draft: format, document, fee, CNR, party, timeline, language
- Returns compliance score + suggestions
- JSONB saved to `ai_suggestions` table
- Catches errors BEFORE court filing
AIPOT-COMMUNICATOR (Priority: 🔴 HIGH
- Reminder schedule: 15 days, 7 days, 48 hours, 24 hours before hearing
- Channels: WhatsApp (primary), SMS (fallback), Email (invoices), Voice (urgent)
- Message templates in EN/HI/PA
- Celery scheduled tasks run every minute
AIPOT-POLICE (Priority: 🟡 MEDIUM
- Health checks every 10 minutes: API, DB, Redis, Kafka, AI server, S3, scraper
- Alert if: response > 500ms, connection fails, scraper silent > 2 hours
- Minor: Slack webhook. Major: SMS to Arjun + Email
AIPOT-BILLING (Priority: 🟡 MEDIUM
- GST-compliant invoices (18% GST)
- Invoice number format: `LETESE.INV-2026-00001`
- PDF generated with WeasyPrint
- Razorpay integration for payments
- Subscription management: Basic/Professional/Elite/Enterprise
AIPOT-RESEARCH (Priority: 🟢 LOW
- Semantic search via pgvector
- All court orders embedded using `all-MiniLM-L6-v2`
- Cosine similarity search
- Returns top 10 results with case citations + excerpts
AIPOT-TRANSLATE (Priority: 🟡 MEDIUM
- Meta MMS fine-tuned model on AI24x7 server
- Languages: English, Hindi, Punjabi
- Preserves PDF/DOCX formatting
- Accuracy score stored in `translation_jobs`
14. Critical Issues to Fix
> As of 27 April 2026
| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| 1 | API Server (port 4007) = ZUMMP API, NOT LETESE | 🔴 CRITICAL | Rebuild LETESE FastAPI from scratch |
| 2 | Super Admin shows 'ZUMMP VORTEQ' instead of 'LETESE' | 🔴 CRITICAL | Replace all mock data + branding |
| 3 | Super Admin nav menu has wrong items (logistics) | 🔴 CRITICAL | Replace with legal-specific menu |
| 4 | Customer Dashboard (app.letese.xyz) has NO backend | 🔴 CRITICAL | Connect to new LETESE API |
| 5 | Pricing mismatch: DB=₹999/2999, Website=₹4999/10999 | 🔴 CRITICAL | Update all 21 DB tables |
| 6 | No Razorpay integration | 🟡 MEDIUM | Build payment flow |
| 7 | No WhatsApp Business API | 🟡 MEDIUM | Connect 360dialog |
| 8 | No court scraper working | 🟡 MEDIUM | Build AIPOT-SCRAPER |
| 9 | No AI drafting engine connected | 🟡 MEDIUM | Connect AI24x7 Qwen3-VL |
| 10 | No mobile app (Flutter not built) | 🟢 LOW | Build after web 15. Entry Flow (New Advocate Joins)
```
Step 1: Visit letese.xyz
         ↓
Step 2: Click 'Sign Up' → Registration form
         Name, Email, Phone, Bar Council Number
         ↓
Step 3: POST /api/auth/register
         → Creates tenant in PostgreSQL
         → Creates Advocate Admin user
         ↓
Step 4: Email OTP verification
         ↓
Step 5: WhatsApp OTP verification (optional)
         ↓
Step 6: Dashboard created
         Default plan = Basic (FREE)
         30 cases, 5GB storage
         ↓
Step 7: Onboarding wizard
         Add firm details, team members, first case
         ↓
Step 8: User clicks "Upgrade to Professional"
         → Razorpay payment page
         → Payment success → Subscription activated
         ↓
Step 9: Full access granted
         All 8 AIPOT agents unlocked
         WhatsApp, SMS, AI drafting, court scraper all active
```
16. Server Resources
Server: 43.242.224.231
| Resource | Status | Available |
|---------|--------|-----------|
| RAM | 1.6GB used / 31GB | ✅ 29GB FREE |
| Disk | 200GB used / 726GB | ✅ 526GB FREE |
| GPU | NVIDIA L4 22GB VRAM | ✅ 16GB FREE |
| GPU Util | 0% (idle) | ✅ Ready for AI |
| GPU Temp | 41°C | ✅ Cool |
| Load Avg | 0.00 | ✅ Idle |
| Docker | ai24x7-factory running | ✅ Healthy |
| Ports | 5050, 5052, 5053, 5054, 5055, 8080 | ✅ Available |
**Current running services:**
- Port 5050: CCTV AI API v10
- Port 5052: Factory Dashboard v6
- Port 5053: License Server v2
- Port 5054: Camera API
- Port 5055: Payment Page
- Port 8080: AI24x7 Qwen3-VL (llama-server)
**LETESE backend recommended ports:** 4001-4006 (or 8000-8005)
Server: 187.127.139.147 (existing infrastructure)
| Resource | Status |
|---------|--------|
| PostgreSQL | ✅ 21 tables, pgvector enabled |
| MongoDB | ✅ Collections ready |
| Redis | ✅ Ready |
| Marketing Website | ✅ Running on port 4009 |
17. Competitor Analysis
| Competitor | Price | AI Drafting | Court Scraper | WhatsApp | Hindi |
|-----------|-------|------------|---------------|----------|-------|
| Cuto.ai | ₹15,000/mo | ❌ | ❌ | ❌ | ❌ |
| Legistify | ₹20,000/mo | Basic | ❌ | ❌ | ❌ |
| Lawrato | ₹10,000/mo | ❌ | ❌ | ❌ | ❌ |
| **LETESE** | **₹4,999/mo** | **✅ Full** | **✅ 25 HCs** | **✅** | **✅** |
**LETESE Advantages:**
- 75% cheaper than competitors
- First-mover in AI-native legal tech for India
- AI runs on own GPU = cost advantage
- Multi-language support (EN/HI/PA) = unique
- Court scraper for all 25 HCs = unique
18. Running Cost
Monthly Expenses (Estimated)
| Item | Cost |
|------|------|
| Server 43.242.224.231 | ₹5,000/mo |
| Server 187.127.139.147 | ₹3,000/mo |
| Kafka + Redis (if managed) | ₹2,000/mo |
| 360dialog WhatsApp | ₹1,000/mo |
| MSG91 SMS | ₹1,000/mo |
| Razorpay fees (2%) | Variable |
| Domain + SSL | ₹500/mo |
| **Total** | **₹12,500-20,000/mo** |
Revenue at Break-even
- 3 Professional users = ₹14,997/mo → covers costs
- 10 Professional users = ₹49,990/mo → profitable
vs Competitors
- Cuto charges ₹15,000/mo → LETESE at ₹4,999 = 3x better value
- No other competitor offers AI drafting + court scraper + WhatsApp at this price
✅ What's Already Done (Documentation)
| File | Content |
|------|---------|
| `letese/docs/01-project-overview.md` | ✅ Product, agents, tech stack, pricing, colors |
| `letese/docs/02-database-schema.md` | ✅ 25 tables, all columns, RLS |
| `letese/docs/03-60-day-build-plan.md` | ✅ Phase 1/2/3 schedule |
| `letese/docs/04-fastapi-backend-structure.md` | ✅ File structure, API routes |
| `letese/docs/05-aipot-agents.md` | ✅ Deep dive all 8 AIPOT agents |
| `letese/docs/15-google-cloud-integration-plan.md` | ✅ GCP setup |
📌 Pending Decisions (From Arjun
1. **Server:** Use 43.242.224.231 for LETESE backend? (Recommended: YES)
2. **AI:** Use AI24x7 Qwen3-VL for drafting? (Recommended: YES, it's FREE)
3. **WhatsApp:** Have 360dialog account? (Need: YES)
4. **Razorpay:** LIVE account ready? (Need: YES)
5. **Super Admin:** Only Arjun or team too?
6. **First court:** P&H HC or Delhi HC? (Recommended: P&H HC first)
7. **Flutter mobile app:** Build after web stable? (Recommended: YES)
*Document prepared by: AI Assistant*
*Last updated: 27 April 2026*
*Version: 1.0*
)stable |
))))))))OW |
DIUM |
sHello from LETESE bot!
This document contains the complete LETESE project documentation.
