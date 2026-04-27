# LETESE — 60-Day Build Plan
## Starting: 27 April 2026

---

## PHASE 1: FOUNDATION (Days 1–15)

### Week 1

| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 1 | Build LETESE FastAPI backend — Auth (Register/Login/JWT/OTP) | 8 | 🔴 HIGH |
| 2 | Build Advocates CRUD + Profile API | 4 | 🔴 HIGH |
| 3 | Build Cases CRUD API | 5 | 🔴 HIGH |
| 4 | Fix Super Admin Dashboard — replace ZUMMP data + branding | 10 | 🔴 HIGH |
| 5 | Connect Customer Dashboard to new LETESE API | 8 | 🔴 HIGH |
| 6 | Align database pricing (₹4,999 / ₹10,999) with website | 2 | 🔴 HIGH |

### Week 2

| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 7 | Install Kafka on server 43.242.224.231 | 3 | 🟡 MEDIUM |
| 8 | Build AIPOT-SCRAPER — P&H HC + Delhi HC | 15 | 🔴 HIGH |
| 9 | Build AIPOT-DRAFT — connect AI24x7 Qwen3-VL | 10 | 🔴 HIGH |
| 10 | Build AIPOT-COMPLIANCE — checklist validation engine | 10 | 🔴 HIGH |
| 11 | Build Clients CRUD API | 3 | 🟡 MEDIUM |
| 12 | Build Documents upload/download API (S3) | 4 | 🟡 MEDIUM |

### Week 3

| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 13 | Build AIPOT-COMMUNICATOR — reminder scheduling | 12 | 🔴 HIGH |
| 14 | Connect 360dialog WhatsApp Business API | 8 | 🔴 HIGH |
| 15 | Razorpay payment integration + GST invoices | 10 | 🔴 HIGH |
| 16 | RBAC — Team roles + permissions (6 roles) | 6 | 🟡 MEDIUM |
| 17 | Build Drafts API + AI draft storage | 4 | 🟡 MEDIUM |

---

## PHASE 2: ADVANCED FEATURES (Days 16–35)

### Week 4

| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 18 | AIPOT-POLICE — System health monitoring (cron) | 8 | 🟡 MEDIUM |
| 19 | AIPOT-RESEARCH — pgvector legal precedent search | 12 | 🟡 MEDIUM |
| 20 | AIPOT-TRANSLATE — EN/HI/PA translation (Meta MMS) | 8 | 🟡 MEDIUM |
| 21 | Client-facing branded portal (white-label subdomain) | 10 | 🟡 MEDIUM |
| 22 | Build Invoices API + WeasyPrint PDF generation | 5 | 🟡 MEDIUM |
| 23 | Build Subscriptions API + plan management | 4 | 🟡 MEDIUM |

### Week 5

| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 24 | Court scraper — Supreme Court + NCDRC | 15 | 🟡 MEDIUM |
| 25 | Calendar + hearing date management UI | 8 | 🟡 MEDIUM |
| 26 | Migrate all LETESE services to server 43.242.224.231 | 6 | 🟡 MEDIUM |
| 27 | Document version history + audit trail | 5 | 🟡 MEDIUM |
| 28 | Court orders API + AI summary generation | 5 | 🟡 MEDIUM |
| 29 | Build Tasks API (to-do items) | 4 | 🟡 MEDIUM |

### Week 6

| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 30 | AIPOT-BILLING — Automated invoice + GST generation | 10 | 🟡 MEDIUM |
| 31 | Full testing + bug fixing | 15 | 🟡 MEDIUM |
| 32 | Performance optimization (query tuning, caching) | 5 | 🟡 MEDIUM |
| 33 | API rate limiting + security hardening | 4 | 🟡 MEDIUM |
| 34 | WebSocket for real-time notifications | 5 | 🟡 MEDIUM |

---

## PHASE 3: MOBILE + DEPLOY (Days 36–60)

### Week 7

| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 35 | Flutter Web build setup | 8 | 🟢 LOW |
| 36 | Flutter Android + iOS build | 12 | 🟢 LOW |
| 37 | Mobile — Login + Dashboard screens | 8 | 🟢 LOW |
| 38 | Mobile — Case list + Case detail screens | 8 | 🟢 LOW |
| 39 | Mobile — Document viewer + uploader | 6 | 🟢 LOW |

### Week 8

| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 40 | Mobile — AI Draft generation screen | 8 | 🟢 LOW |
| 41 | Mobile — Translation screen | 7 | 🟢 LOW |
| 42 | Mobile — Client management | 5 | 🟢 LOW |
| 43 | Deploy to production (letese.xyz, app.letese.xyz, admin.letese.xyz) | 10 | 🟢 LOW |
| 44 | SSL certificates + CDN + domain setup | 5 | 🟢 LOW |
| 45 | CI/CD pipeline (GitHub Actions) | 5 | 🟢 LOW |

### Week 9

| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 46 | User acceptance testing (UAT) with real advocates | 15 | 🟢 LOW |
| 47 | Bug fixes + final polish | 15 | 🟢 LOW |
| 48 | Documentation + API docs (Swagger/OpenAPI) | 5 | 🟢 LOW |
| 49 | Launch checklist + monitoring setup | 5 | 🟢 LOW |

---

## IMMEDIATE ACTIONS (This Week)

| # | Task | Decision Needed |
|---|------|----------------|
| A | Confirm: Server 43.242.224.231 to host LETESE backend? | YES/NO |
| B | Confirm: Use AI24x7 Qwen3-VL for AIPOT-DRAFT (saves API cost)? | YES/NO |
| C | Confirm: WhatsApp Business — do you have 360dialog account? | YES/NO |
| D | Confirm: Razorpay account ready for LIVE payments? | YES/NO |
| E | Confirm: Flutter for mobile app (web + Android + iOS)? | YES/NO |
| F | Who is the REAL Super Admin? Only Arjun or team too? | Clarify |
| G | What are the FIRST 3 courts to scrape? | P&H HC priority |

---

## Estimated Monthly Running Cost

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
