# LETESE — Complete Project Documentation

> Legal Tech SaaS Platform for Indian Advocates | Company: GOUP Consultancy Services LLP
> Last Updated: 27 April 2026

---

## 📁 Folder Structure

```
letese/
│
├── README.md                    ← YOU ARE HERE (master index)
│
├── docs/                       ← All documentation files (MD format)
│   │
│   ├── 00-complete-documentation.md    ← MASTER DOC (all-in-one)
│   ├── 01-project-overview.md          ← What is LETESE, 8 AIPOT agents
│   ├── 02-database-schema.md           ← 25 tables, all columns
│   ├── 03-60-day-build-plan.md        ← Phase 1/2/3 schedule
│   ├── 04-fastapi-backend-structure.md ← File tree, API routes
│   ├── 05-aipot-agents.md             ← Deep dive all 8 agents
│   ├── 06-realistic-timeline-and-architecture.md ← Architecture, 90-day plan
│   └── 15-google-cloud-integration-plan.md ← GCP setup
│
├── google-docs-export/          ← Google Docs backups (live synced)
│   ├── LETESE-Complete-Documentation.md       ← Live Google Doc #1
│   ├── LETESE-Google-AI-Integration-Plan.md   ← Live Google Doc #2
│   └── LETESE-Google-API-Requirements.md      ← Live Google Doc #3
│
├── contracts/                  ← Technical contracts & specs
│   ├── (auth schema, API specs, AIPOT protocols)
│
├── backend/                    ← FastAPI backend (to be built)
│
├── frontend/                   ← Flutter/Web frontend (to be built)
│
└── infrastructure/            ← Docker, CI/CD, server configs
```

---

## 🌐 Live Google Docs (Fully Editable)

| Document | URL | Purpose |
|----------|-----|---------|
| **Main Documentation** | https://docs.google.com/document/d/1Ei9K2fnqZDVQLbuNikZPVJh5SEVA0G9mETk2RQjaKyw/edit | Full project docs (6 parts) |
| **Google AI Integration Plan** | https://docs.google.com/document/d/1VQmg8JcsFzXnf3usvL0348vniAvhEI0nSopgPdwSeag/edit | For Google team |
| **API Requirements Checklist** | https://docs.google.com/document/d/1jdI0SjKo95VQDOiKT-L8MmjB5zl64CCXqa-kFDKRUHo/edit | What we need from Google |

---

## 🎯 What is LETESE?

**LETESE** = **LE**gal **TE**ch **SE**rvices  
AI-powered Legal Practice Management SaaS for Indian advocates.

**8 AIPOT Agents (AI Process & Operations Technology):**
- 🤖 AIPOT-SCRAPER — Court portal monitoring 24/7
- 🤖 AIPOT-DRAFT — AI petition drafting (5-minute drafts)
- 🤖 AIPOT-COMPLIANCE — Draft validation (7 checks)
- 🤖 AIPOT-COMMUNICATOR — WhatsApp/SMS/Email/Voice reminders
- 🤖 AIPOT-POLICE — System health monitoring
- 🤖 AIPOT-BILLING — GST invoices + Razorpay
- 🤖 AIPOT-RESEARCH — Legal precedent search (pgvector)
- 🤖 AIPOT-TRANSLATE — EN/HI/PA translation

**Platform:** Multi-tenant SaaS | **URLs:** letese.xyz, app.letese.xyz, admin.letese.xyz

---

## ⚠️ Critical Issues (Must Fix First)

| # | Issue | Severity |
|---|-------|----------|
| 1 | Port 4007 API = ZUMMP API (NOT LETESE) | 🔴 CRITICAL |
| 2 | Super Admin shows 'ZUMMP VORTEQ' instead of 'LETESE' | 🔴 CRITICAL |
| 3 | Customer Dashboard has NO backend connection | 🔴 CRITICAL |
| 4 | Pricing mismatch: DB=₹999, Website=₹4,999 | 🔴 CRITICAL |

---

## 🚀 Build Status

| Phase | Status | Notes |
|-------|--------|-------|
| Documentation | ✅ DONE | 8 docs, 3 Google Docs |
| DB Schema | ✅ DOCUMENTED | 25 tables in docs |
| FastAPI Backend | ⏳ PENDING | Phase 0 to start |
| AI Integration | ⏳ PENDING | Google Gemini pending |
| Frontend | ⏳ PENDING | Flutter app pending |
| Court Scraper | ⏳ PENDING | AIPOT-SCRAPER pending |
| Billing | ⏳ PENDING | Razorpay pending |

---

## 📊 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React SPA + Flutter Web+Mobile |
| Backend | Python FastAPI |
| Database | PostgreSQL + pgvector |
| AI | AI24x7 Qwen3-VL-8B (FREE) + Google Gemini (planned) |
| Cache | Redis |
| Queue | Kafka |
| File Storage | S3 / Local Disk |
| WhatsApp | 360dialog BSP |
| SMS | MSG91 |
| Payments | Razorpay |

---

## 📅 Realistic Timeline

- **Week 1-2:** Documentation + Phase 0 (DB + Auth)
- **Week 3-4:** Core API (Cases, Hearings, Documents)
- **Week 5-7:** 4 AIPOT Agents (Draft, Compliance, Communicator, Scraper)
- **Week 8-10:** Billing, Research, Translate
- **Week 11-12:** Super Admin + Client Portal
- **Week 13:** Hardening + Deploy

**Total: ~90 Days (3 months)**

---

## 🔑 Key Contacts

- **Project Lead:** Arjun Singh
- **Email:** arjun.raghav93@gmail.com
- **Company:** GOUP Consultancy Services LLP
- **Website:** https://letese.xyz
- **Server:** 43.242.224.231 (NVIDIA L4 GPU)

---

*This README is the master index. Start here.*
