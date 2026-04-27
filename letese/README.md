# LETESE — Legal Practice Management SaaS

> AI-powered legal practice management platform for Indian advocates and law firms.

**Version:** 1.0 | **Date:** 27 April 2026 | **Company:** GOUP Consultancy Services LLP

---

## 🌐 Three-URL Ecosystem

| URL | Purpose | Tech | Status |
|-----|---------|------|--------|
| [letese.xyz](https://letese.xyz) | Marketing Website | React SPA | ✅ Needs branding fix |
| [app.letese.xyz](https://app.letese.xyz) | Advocate Dashboard | Flutter Web+App | 🔴 NO backend |
| [admin.letese.xyz](https://admin.letese.xyz) | Super Admin | Flutter Web+App | 🔴 WRONG DATA |

---

## 📁 Documentation Index

| File | Contents |
|------|---------|
| `docs/01-project-overview.md` | Product, AIPOT agents, tech stack, pricing, brand colors |
| `docs/02-database-schema.md` | 25 PostgreSQL tables, all columns, enums, RLS |
| `docs/03-60-day-build-plan.md` | Week-by-week 60-day build schedule |
| `docs/04-fastapi-backend-structure.md` | Backend file structure, all API routes |
| `docs/05-aipot-agents.md` | Deep dive on all 8 AIPOT agents |

---

## 8 AIPOT Agents

| Agent | Function | Priority |
|-------|----------|----------|
| 🤖 **AIPOT-SCRAPER** | Court portal monitoring 24/7 | 🔴 HIGH |
| 🤖 **AIPOT-DRAFT** | AI petition drafting (Qwen3-VL) | 🔴 HIGH |
| 🤖 **AIPOT-COMPLIANCE** | Draft validation + checklist | 🔴 HIGH |
| 🤖 **AIPOT-COMMUNICATOR** | WhatsApp/SMS/Email/Voice reminders | 🔴 HIGH |
| 🤖 **AIPOT-POLICE** | System health monitoring | 🟡 MEDIUM |
| 🤖 **AIPOT-BILLING** | Invoice + GST + Razorpay | 🟡 MEDIUM |
| 🤖 **AIPOT-RESEARCH** | pgvector legal search | 🟢 LOW |
| 🤖 **AIPOT-TRANSLATE** | EN/HI/PA translation | 🟡 MEDIUM |

---

## Tech Stack

| Layer | Technology | Location |
|-------|-----------|----------|
| Backend | Python FastAPI | 43.242.224.231 (REBUILD) |
| Database | PostgreSQL + pgvector | 187.127.139.147:5433 |
| Real-time | MongoDB | 187.127.139.147:27018 |
| Cache | Redis | 187.127.139.147:6379 |
| Queue | Kafka | 43.242.224.231 (to install) |
| AI | Qwen3-VL-8B | 43.242.224.231:8080 |
| Payments | Razorpay | To connect |
| WhatsApp | 360dialog BSP | To connect |
| SMS | MSG91 | To connect |

---

## Critical Issues (MUST FIX FIRST)

1. 🔴 API Server (port 4007) = ZUMMP API — REBUILD NEEDED
2. 🔴 Super Admin shows ZUMMP data — FIX BRANDING
3. 🔴 Customer Dashboard has NO backend connection
4. 🔴 Pricing mismatch in DB (₹999/₹2999 vs ₹4999/₹10999)

---

## Running Cost

- **Server:** ₹0 (already paid)
- **AI:** ₹0 (your GPU)
- **Total:** ₹8,000–20,000/mo
- **vs Competition:** ₹20,000+/mo

---

## Status

🟡 **PLANNING COMPLETE** — Ready to build
