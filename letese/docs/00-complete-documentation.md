# LETESE — Complete Project Documentation
> Version 1.0 | Date: 27 April 2026 | Owner: Arjun Singh | Company: GOUP Consultancy Services LLP

---

## 📋 Table of Contents

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

---

## 1. Project Overview

### What is LETESE?

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

---

## 2. Problem Statement

### Pain Points for Indian Advocates

| Problem | Impact |
|---------|--------|
| Manual case tracking (Excel/physical diary) | Cases missed, clients unhappy |
| No court order monitoring | Important orders missed |
| Hours spent drafting petitions | Billable time lost |
| Client reminder failures | Court appearances missed |
| Manual invoicing | Cash flow problems |
| Language barriers (HI/PA/EN) | Communication gaps |
| High software costs (₹20,000+/month) | Unaffordable for small firms |

### Current Market Gap

- Existing tools: Complex, expensive, not AI-native
- Cuto, Legistify, Lawrato: Generic, no court integration
- No tool has: AI drafting + court scraper + multi-language + affordable pricing
- **LETESE fills this gap** with 8 AI agents + ₹4,999/month pricing

---

## 3. Our Solution

### LETESE vs Traditional Practice Management

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

### Competitive Advantage

- **AI24x7 Qwen3-VL-8B** runs on our own GPU server = ₹0 AI cost
- Competitors pay ₹0.50/1000 tokens to OpenAI
- We can pass savings to users = lower pricing
- All AI processing happens in India (data sovereignty)

---

## 4. Eight AIPOT Agents

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
| 8 | **AIPOT-TRANSLATE** | Multilingual legal translation EN/HI/PA (Meta MMS) | 🟡 MEDIUM |

---

## 5. Tech Stack

### Frontend
| Layer | Technology | Notes |
|-------|-----------|-------|
| Marketing Website | React SPA | Hosted at 187.127.139.147:4009 |
| Customer App | Flutter Web + Mobile | To be built |
| Admin Dashboard | React | admin.letese.xyz |
| Design System | Glassmorphism 2.0 | Dark theme, glass cards |

### Backend
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

### External Integrations
| Service | Provider | Purpose |
|---------|----------|---------|
| WhatsApp | 360dialog BSP | Client communications |
| SMS | MSG91 | Fallback alerts |
| Email | SendGrid | Formal notices, invoices |
| Payments | Razorpay | Subscription billing |
| Voice | ElevenLabs / AI24x7 TTS | AI voice calls |
| AI | AI24x7 Qwen3-VL | Drafting + Research + Translation |

### Court Portals (AIPOT-SCRAPER targets)
| Court | URL | Priority |
|-------|-----|----------|
| Supreme Court of India | main.sci.gov.in | 🔴 HIGH |
| Punjab & Haryana HC | phhc.gov.in | 🔴 HIGH |
| Delhi High Court | delhihighcourt.nic.in | 🔴 HIGH |
| NCDRC | ncdrc.nic.in | 🟡 MEDIUM |
| Bombay High Court | bombayhighcourt.nic.in | 🟡 MEDIUM |
| All other 20 HCs | individual portals | 🟢 LOW |

---

## 6. Database Schema (25 Tables)

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

---

## 7. User Roles & Access

| Role | Who | Access | Dashboard |
|------|-----|--------|-----------|
| **Super Admin** | LETESE Team (Arjun) | Full system, all tenants, billing, config | admin.letese.xyz |
| **Advocate Admin** | Law Firm Owner | Full access to own firm | app.letese.xyz |
| **Advocate** | Senior Advocate | Own cases, all features | app.letese.xyz |
| **Clerk** | Court Clerk | Create/view cases, upload docs | app.letese.xyz |
| **Paralegal** | Junior Lawyer | Clerk + trigger communications | app.letese.xyz |
| **Intern** | Law Student | View assigned cases only | app.letese.xyz |
| **Client** | End Client | Own case status, documents, reminders | Branded portal (subdomain) |

### Client White-Label Portal
- Each law firm gets a branded portal: `firmname.letese.xyz`
- Clients see only their own cases
- No access to firm data or other clients
- Full mobile responsiveness

---

## 8. Multi-Tenant SaaS Architecture

**Concept:** ONE PostgreSQL database, ONE schema, MULTIPLE tenants (law firms)

```
PostgreSQL Database (187.127.139.147:5433)
├── tenant_id = "firm_uuid_1" → Law Firm A's data
├── tenant_id = "firm_uuid_2" → Law Firm B's data
└── tenant_id = "firm_uuid_3" → Law Firm C's data

All queries filtered by tenant_id from JWT token
Row-Level Security (RLS) enforces isolation at DB level
```

### Isolation Strategy

| Resource | Strategy |
|---------|----------|
| PostgreSQL | RLS (Row-Level Security) on all tables |
| S3 Storage | One folder per tenant: `s3://letese-docs/tenant_uuid/` |
| Redis | Keys prefixed: `session:tenant_uuid:user_id` |
| Kafka | Topics namespaced: `letese.{tenant_id}.scraper.jobs` |
| AI Processing | Tenant context passed in every API call |

---

## 9. Pricing Plans (CORRECT — per website)

> ⚠️ Database currently has wrong pricing (₹999/₹2,999). Must update.

| Plan | Monthly | Annual | Cases | Storage | Features |
|------|---------|--------|-------|---------|---------|
| **Basic** | FREE | — | 30 | 5 GB | Email reminders, case tracking |
| **Professional** | ₹4,999 | ₹3,999/mo | 200 | 50 GB | SMS + WhatsApp, billing, 3 seats |
| **Elite** | ₹10,999 | ₹8,999/mo | 500 | 200 GB | AI drafting, HC/SC checklist, translation, voice |
| **Enterprise** | Custom | — | Unlimited | Unlimited | All AIPOTs, API access, white-label, dedicated manager |

### Plan Upgrade Flow
1. User signs up → Basic (FREE) plan
2. User clicks "Upgrade" → Razorpay payment page
3. Payment success → Subscription activated
4. All features of plan unlocked instantly

---

## 10. Brand Guidelines

### Colors (Glassmorphism 2.0)

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

### Typography
- Headings: Inter / Poppins
- Body: Inter
- Monospace (code): JetBrains Mono

### Logo Concept
```
[LETESE] — Legal Tech Services
 ● (green dot after LETESE text)
```

### Design Reference
- Dark glassmorphism theme
- Free template: templatemo.com/tm-607-glass-admin
- Competitor reference: Clio.com (gold standard legal SaaS)

---

## 11. 60-Day Build Plan

> Full plan: `letese/docs/03-60-day-build-plan.md`

### Phase 1 — Foundation (Days 1-20)
- [ ] Rebuild LETESE FastAPI backend from scratch
- [ ] Fix database pricing, branding, all ZUMMP references
- [ ] Connect PostgreSQL (21 existing tables)
- [ ] User authentication (signup/login/JWT)
- [ ] Case management CRUD
- [ ] Document upload (S3/local)
- [ ] Super Admin dashboard (admin.letese.xyz)

### Phase 2 — AI + Communications (Days 21-40)
- [ ] Connect AI24x7 Qwen3-VL at port 8080
- [ ] AIPOT-DRAFT: AI petition generation
- [ ] AIPOT-COMPLIANCE: Draft validation
- [ ] AIPOT-COMMUNICATOR: WhatsApp (360dialog)
- [ ] Reminder system (15d/7d/48h/24h)
- [ ] Email integration (SendGrid)
- [ ] SMS integration (MSG91)

### Phase 3 — Courts + Billing (Days 41-60)
- [ ] AIPOT-SCRAPER: P&H HC + Delhi HC scraper
- [ ] Kafka queue setup for scraper workers
- [ ] AIPOT-BILLING: Razorpay + GST invoices
- [ ] Subscription management
- [ ] AIPOT-RESEARCH: pgvector semantic search
- [ ] AIPOT-TRANSLATE: EN/HI/PA translation
- [ ] Client white-label portal
- [ ] Flutter mobile app (basic)

---

## 12. FastAPI Backend Structure

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

### Key API Endpoints
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

---

## 13. AIPOT Agents Deep Dive

> Full details: `letese/docs/05-aipot-agents.md`

### AIPOT-SCRAPER (Priority: 🔴 HIGH)
- Monitors court portals every 15 minutes using Playwright
- Kafka queue: `letese.scraper.jobs`
- CNR format validation (SC-YYYY-NNNN, CRM-M-YYYY-NNNNN, etc.)
- Dedup via SHA256 hash of order text
- On new order → notify advocate via AIPOT-COMMUNICATOR

### AIPOT-DRAFT (Priority: 🔴 HIGH)
- Advocate enters case details → 5-minute AI draft
- Connected to AI24x7 Qwen3-VL at `43.242.224.231:8080`
- Supported: CWP, CRM, CRP, Writ, CS, SLP, Consumer Complaint
- Output: .docx + .pdf, formatted as per court rules
- Triggers AIPOT-COMPLIANCE after generation

### AIPOT-COMPLIANCE (Priority: 🔴 HIGH)
- Runs 7 checks on every draft: format, document, fee, CNR, party, timeline, language
- Returns compliance score + suggestions
- JSONB saved to `ai_suggestions` table
- Catches errors BEFORE court filing

### AIPOT-COMMUNICATOR (Priority: 🔴 HIGH)
- Reminder schedule: 15 days, 7 days, 48 hours, 24 hours before hearing
- Channels: WhatsApp (primary), SMS (fallback), Email (invoices), Voice (urgent)
- Message templates in EN/HI/PA
- Celery scheduled tasks run every minute

### AIPOT-POLICE (Priority: 🟡 MEDIUM)
- Health checks every 10 minutes: API, DB, Redis, Kafka, AI server, S3, scraper
- Alert if: response > 500ms, connection fails, scraper silent > 2 hours
- Minor: Slack webhook. Major: SMS to Arjun + Email

### AIPOT-BILLING (Priority: 🟡 MEDIUM)
- GST-compliant invoices (18% GST)
- Invoice number format: `LETESE.INV-2026-00001`
- PDF generated with WeasyPrint
- Razorpay integration for payments
- Subscription management: Basic/Professional/Elite/Enterprise

### AIPOT-RESEARCH (Priority: 🟢 LOW)
- Semantic search via pgvector
- All court orders embedded using `all-MiniLM-L6-v2`
- Cosine similarity search
- Returns top 10 results with case citations + excerpts

### AIPOT-TRANSLATE (Priority: 🟡 MEDIUM)
- Meta MMS fine-tuned model on AI24x7 server
- Languages: English, Hindi, Punjabi
- Preserves PDF/DOCX formatting
- Accuracy score stored in `translation_jobs`

---

## 14. Critical Issues to Fix

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
| 10 | No mobile app (Flutter not built) | 🟢 LOW | Build after web stable |

---

## 15. Entry Flow (New Advocate Joins)

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

---

## 16. Server Resources

### Server: 43.242.224.231

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

### Server: 187.127.139.147 (existing infrastructure)

| Resource | Status |
|---------|--------|
| PostgreSQL | ✅ 21 tables, pgvector enabled |
| MongoDB | ✅ Collections ready |
| Redis | ✅ Ready |
| Marketing Website | ✅ Running on port 4009 |

---

## 17. Competitor Analysis

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

---

## 18. Running Cost

### Monthly Expenses (Estimated)

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

### Revenue at Break-even
- 3 Professional users = ₹14,997/mo → covers costs
- 10 Professional users = ₹49,990/mo → profitable

### vs Competitors
- Cuto charges ₹15,000/mo → LETESE at ₹4,999 = 3x better value
- No other competitor offers AI drafting + court scraper + WhatsApp at this price

---

## ✅ What's Already Done (Documentation)

| File | Content |
|------|---------|
| `letese/docs/01-project-overview.md` | ✅ Product, agents, tech stack, pricing, colors |
| `letese/docs/02-database-schema.md` | ✅ 25 tables, all columns, RLS |
| `letese/docs/03-60-day-build-plan.md` | ✅ Phase 1/2/3 schedule |
| `letese/docs/04-fastapi-backend-structure.md` | ✅ File structure, API routes |
| `letese/docs/05-aipot-agents.md` | ✅ Deep dive all 8 AIPOT agents |
| `letese/docs/15-google-cloud-integration-plan.md` | ✅ GCP setup |

## 📌 Pending Decisions (From Arjun)

1. **Server:** Use 43.242.224.231 for LETESE backend? (Recommended: YES)
2. **AI:** Use AI24x7 Qwen3-VL for drafting? (Recommended: YES, it's FREE)
3. **WhatsApp:** Have 360dialog account? (Need: YES)
4. **Razorpay:** LIVE account ready? (Need: YES)
5. **Super Admin:** Only Arjun or team too?
6. **First court:** P&H HC or Delhi HC? (Recommended: P&H HC first)
7. **Flutter mobile app:** Build after web stable? (Recommended: YES)

---

*Document prepared by: AI Assistant*
*Last updated: 27 April 2026*
*Version: 1.0*