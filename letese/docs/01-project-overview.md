# LETESE — Complete Project Overview

> Version 1.0 | Date: 27 April 2026 | Company: GOUP Consultancy Services LLP

---

## What is LETESE?

**LETESE** is an AI-powered Legal Practice Management SaaS platform for advocates, law firms, and legal professionals in India. It automates case management, court monitoring, AI drafting, and client communications — all in one platform.

**Website:** https://letese.xyz
**Marketing:** React SPA at `187.127.139.147:4009`
**App:** app.letese.xyz (Flutter Web + Mobile)
**Admin:** admin.letese.xyz (Super Admin — LETESE team)

---

## The 8 AIPOT Agents (AI Process & Operations Technology)

| Agent | Purpose | Tech | Priority |
|-------|---------|------|----------|
| **AIPOT-SCRAPER** | Monitor court portals 24/7, detect new orders | Playwright + Kafka | 🔴 HIGH |
| **AIPOT-DRAFT** | AI petition drafting using Qwen3-VL-8B | AI24x7 Qwen3-VL | 🔴 HIGH |
| **AIPOT-COMPLIANCE** | Validate drafts against court checklists | spaCy NLP + rule engine | 🔴 HIGH |
| **AIPOT-COMMUNICATOR** | Send WhatsApp/SMS/Email/Voice reminders | 360dialog + MSG91 + SendGrid | 🔴 HIGH |
| **AIPOT-POLICE** | System health monitoring | Python health checks (cron) | 🟡 MEDIUM |
| **AIPOT-BILLING** | Invoice generation, GST, Razorpay | Razorpay API + WeasyPrint | 🟡 MEDIUM |
| **AIPOT-RESEARCH** | Legal precedent search (pgvector) | pgvector semantic search | 🟢 LOW |
| **AIPOT-TRANSLATE** | EN/HI/PA legal translation | AI24x7 Meta MMS | 🟡 MEDIUM |

**Running Cost Advantage:** AI24x7 Qwen3-VL runs on YOUR GPU (43.242.224.231) = ₹0 for AI vs competitors charging ₹20,000+/mo

---

## User Roles & Access

| Role | Who | Access Level | Dashboard |
|------|-----|-------------|-----------|
| Super Admin | LETESE Team (Arjun) | Full system, all tenants | admin.letese.xyz |
| Advocate Admin | Law Firm Owner | Full access to own firm data | app.letese.xyz |
| Advocate | Senior Advocate | Own cases full access | app.letese.xyz |
| Clerk | Court Clerk | Create/view cases, upload docs | app.letese.xyz |
| Paralegal | Junior Lawyer | Clerk + trigger communications | app.letese.xyz |
| Intern | Law Student | View assigned cases only | app.letese.xyz |
| Client | End Client | Own case status, documents, reminders | Branded Portal |

---

## Tech Stack

| Layer | Technology | Location |
|-------|-----------|----------|
| Frontend (Marketing) | React SPA | 187.127.139.147:4009 |
| Frontend (App) | Flutter Web + Mobile | To be built |
| Backend API | Python FastAPI | 43.242.224.231 (REBUILD NEEDED) |
| Database | PostgreSQL + pgvector | 187.127.139.147:5433 |
| Real-time DB | MongoDB | 187.127.139.147:27018 |
| Cache | Redis | 187.127.139.147:6379 |
| Message Queue | Kafka | 43.242.224.231 (to be installed) |
| AI Server | Qwen3-VL-8B | 43.242.224.231:8080 |
| File Storage | S3 / Local Disk | 43.242.224.231 |
| WhatsApp | 360dialog BSP | To connect |
| SMS | MSG91 | To connect |
| Payments | Razorpay | To connect |
| Voice | ElevenLabs / AI24x7 TTS | 43.242.224.231 |

---

## Pricing Plans (CORRECT)

| Plan | Monthly | Annual | Cases | Storage |
|------|---------|--------|-------|---------|
| Basic | FREE | — | 30 | 5 GB |
| Professional | ₹4,999 | ₹3,999/mo | 200 | 50 GB |
| Elite | ₹10,999 | ₹8,999/mo | 500 | 200 GB |
| Enterprise | Custom | — | Unlimited | Unlimited |

⚠️ **ACTION REQUIRED:** Database currently has wrong pricing (₹999/₹2,999). Must update to match website.

---

## Brand Colors (Glassmorphism 2.0)

| Element | Color | Usage |
|---------|-------|-------|
| Brand Blue | `#1A4FBF` | Logo, primary buttons, header |
| Brand Green | `#22C55E` | Logo dot ●, success states, CTAs |
| Neon Cyan | `#00D4FF` | Interactive highlights, links |
| Electric Purple | `#8B5CF6` | AI elements, premium features |
| Page BG | `#0A0E1A` | Deep space background |
| Glass Card BG | `rgba(255,255,255,0.05)` | All cards with blur |
| Text Primary | `#F0F4FF` | Main text |
| Text Secondary | `#8899BB` | Secondary labels |

---

## Multi-Tenant Architecture

**Concept:** ONE database, ONE schema, MULTIPLE tenants (law firms)

- Each tenant has: `tenant_id` (UUID), plan, storage_quota, case_limit
- All queries filtered by `tenant_id` in JWT token
- Row-Level Security (RLS) in PostgreSQL enforces tenant isolation
- S3 bucket: one folder per tenant (`s3://letese-docs/tenant_uuid/`)
- Redis: keys prefixed with `tenant_id` (e.g., `session:tenant_uuid:user_id`)
- Kafka: topics namespaced (`letese.{tenant_id}.scraper.jobs`)

---

## Entry Flow (New Advocate Joins)

1. Advocate visits letese.xyz → Landing page with pricing + features
2. Clicks 'Sign Up' → Registration: Name, Email, Phone, Bar Council No.
3. `POST /api/auth/register` → Creates tenant in PostgreSQL
4. Email verification → OTP sent to email
5. WhatsApp verification → OTP sent to phone
6. Dashboard created → Tenant workspace, default plan = Basic
7. Onboarding wizard → Add firm details, team members, first case
8. Choose plan → Upgrade to Professional/Elite via Razorpay
9. Full access granted → All features of chosen plan unlocked

---

## Critical Issues (As of 27 April 2026)

| Issue | Severity | Fix |
|-------|----------|-----|
| API Server (port 4007) = ZUMMP API, NOT LETESE | 🔴 CRITICAL | Rebuild LETESE FastAPI from scratch |
| Super Admin shows 'ZUMMP VORTEQ' instead of 'LETESE' | 🔴 CRITICAL | Replace all mock data + branding |
| Super Admin nav menu has wrong items (logistics) | 🔴 CRITICAL | Replace with legal-specific menu |
| Customer Dashboard has NO backend connection | 🔴 CRITICAL | Connect to new LETESE API |
| Pricing mismatch: DB=₹999/2999, Website=₹4999/10999 | 🔴 CRITICAL | Update DB plans |
| No Razorpay integration | 🟡 MEDIUM | Build payment flow |
| No WhatsApp Business API | 🟡 MEDIUM | Connect 360dialog |
| No court scraper working | 🟡 MEDIUM | Build AIPOT-SCRAPER |
| No AI drafting engine connected | 🟡 MEDIUM | Connect AI24x7 Qwen3-VL |
| No mobile app (Flutter not built) | 🟢 LOW | Build after web stable |

---

## Reusable Components (Already Exist)

| Component | Reuse? | Notes |
|-----------|--------|-------|
| PostgreSQL schema (21 tables) | ✅ YES | Fix pricing, add missing columns |
| pgvector extension | ✅ YES | Perfect for legal research AI |
| MongoDB collections | ✅ YES | activity logs, scraper logs |
| Redis setup | ✅ YES | No changes needed |
| Marketing website UI | ✅ YES | Good base, just fix branding |
| Dashboard UI shells | ✅ YES | React components can be reused |
| Glassmorphism CSS design | ✅ YES | Excellent design system |

---

## Server 43.242.224.231 — Resources Available

| Resource | Needed | Available |
|---------|--------|-----------|
| RAM | 4GB for FastAPI | ✅ 29GB FREE |
| GPU VRAM | 6GB for Qwen3-VL | ✅ 16GB FREE |
| Disk | Large for files | ✅ 526GB FREE |
| Kafka Workers | 2GB each, 5+ scrapers | ✅ Can run many |

**Estimated Monthly Running Cost:** ₹8,000–20,000/mo (vs competitors at ₹20,000+/mo)
