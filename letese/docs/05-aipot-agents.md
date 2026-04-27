# LETESE — 8 AIPOT Agents Deep Dive

> AI Process & Operations Technology

---

## AIPOT-SCRAPER 🔴 HIGH PRIORITY
**Monitor court portals 24/7, detect new orders**

### Purpose
Automatically scrape court portals for new orders and case updates. Notify advocates immediately when something new appears.

### Courts to Cover (Priority Order)
| Court | URL | CNR Format | Difficulty |
|-------|-----|-----------|------------|
| Supreme Court of India | main.sci.gov.in | SC-YYYY-NNNN | MEDIUM |
| Punjab & Haryana HC | phhc.gov.in | CRM-M-YYYY-NNNNN | MEDIUM |
| Delhi High Court | delhihighcourt.nic.in | WPD-MC-YYYY-NNNNN | MEDIUM |
| NCDRC | ncdrc.nic.in | Consumer Petition | HARD (CAPTCHA) |
| Bombay High Court | bombayhighcourt.nic.in | WP-L-YYYY-NNNNN | MEDIUM |
| All 25 High Courts | individual | Varies | HARD |

### Tech Stack
- **Scraping:** Playwright (headless browser) for JavaScript-rendered portals
- **Queue:** Kafka (`letese.scraper.jobs`)
- **Proxy:** Rotating proxy for rate limiting compliance
- **Dedup:** SHA256 hash of order text stored in `court_orders.order_hash`

### Flow
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

### CNR Format Examples
```
SC-2025-1234           → Supreme Court
CRM-M-2025-12345       → P&H HC
WPD-MC-2025-1234       → Delhi HC
WP-L-2025-12345        → Bombay HC
```

---

## AIPOT-DRAFT 🔴 HIGH PRIORITY
**AI petition drafting using Qwen3-VL-8B**

### Purpose
Generate legal petitions in minutes instead of hours. Advocate enters case details → AI produces formatted draft.

### Supported Petition Types
| Petition | Court | Format |
|----------|-------|--------|
| CWP (Civil Writ Petition) | P&H HC | Standard writ format |
| CRM (Criminal Misc.) | P&H HC | Criminal format |
| CRP (Civil Revisional) | P&H HC | Revisional format |
| Writ Petition | Delhi HC | Article 226 format |
| CS (Civil Suit) | Delhi HC | Civil suit format |
| SLP (Special Leave) | Supreme Court | SLP format |
| Consumer Complaint | NCDRC | Consumer protection format |

### Tech Stack
- **Model:** AI24x7 Qwen3-VL-8B at `43.242.224.231:8080`
- **Pipeline:** LangChain for prompt templating
- **Document:** python-docx for .docx output, WeasyPrint for PDF

### Prompt Template
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

### Flow
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

---

## AIPOT-COMPLIANCE 🔴 HIGH PRIORITY
**Validate drafts against court checklists**

### Purpose
Catch errors before filing. Run automated checks on AI-generated drafts.

### Check Types
| Check | What it validates |
|-------|------------------|
| Format Check | Page limits, font size (12pt), margins (1 inch) |
| Document Check | Vakalatnama, affidavit, index attached |
| Fee Check | Court fee stamp duty paid |
| CNR Check | Correct CNR number format |
| Party Check | All parties named correctly in cause list |
| Timeline Check | Within limitation period (Article 137, etc.) |
| Language Check | Hindi/English compliance |

### Compliance Report (JSONB saved)
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

---

## AIPOT-COMMUNICATOR 🔴 HIGH PRIORITY
**Send reminders via WhatsApp/SMS/Email/Voice**

### Purpose
Auto-remind clients and advocates about hearings at 15 days, 7 days, 48 hours, and 24 hours before.

### Channels
| Channel | Provider | Use Case |
|---------|----------|----------|
| WhatsApp | 360dialog BSP | Primary — rich messages, templates |
| SMS | MSG91 | Fallback / urgent alerts |
| Email | SendGrid | Invoices, formal notices |
| Voice | AI24x7 TTS | Hearing reminders (AI calls) |

### Reminder Schedule
```
Case hearing: March 15, 2026 at 10:00 AM

15 days before  → WhatsApp: "Reminder: Hearing on Mar 15 in CNR XYZ"
7 days before   → WhatsApp + SMS: "Urgent: Hearing in 1 week"
48 hours before → WhatsApp + SMS + Email
24 hours before → WhatsApp + SMS + Voice call (AI)
```

### Message Templates (WhatsApp)
```
15_day: "🗓️ *Reminder:* Hearing on {date} at {time} in {court}. Case: {case_no}. - LETESE"
7_day: "⚠️ *Urgent:* Hearing in 7 days — {date}, {time} at {court}. Case: {case_no}. Prepare all documents. - LETESE"
48_hour: "🚨 *48 hours:* Hearing tomorrow at {time}. Court: {court}. Case: {case_no}. - LETESE"
24_hour: "📞 *AI Call:* Your hearing is tomorrow at {time}. Please confirm availability. - LETESE"
```

---

## AIPOT-POLICE 🟡 MEDIUM
**System health monitoring**

### Purpose
Ensure all systems are running. Alert if something breaks.

### Checks (every 10 min / 60 min)
| Check | What | Alert if |
|-------|------|----------|
| API Health | GET /health | Response > 500ms or 5xx |
| Database | SELECT 1 | Connection fails |
| Redis | PING | Not responding |
| Kafka | Consumer lag | > 1000 messages pending |
| AI Server | GET /v1/models | Model not loaded |
| S3 Storage | List buckets | Access denied |
| Scraper | Last successful scrape | > 2 hours ago |

### Alerts
- Minor: Slack/Discord webhook
- Major: SMS to Arjun + Email

---

## AIPOT-BILLING 🟡 MEDIUM
**Automated invoices + GST + Razorpay**

### Purpose
Generate GST-compliant invoices automatically. Handle subscription billing.

### Invoice Format (per GST rules)
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

### Flow
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

---

## AIPOT-RESEARCH 🟢 LOW
**Legal precedent search using pgvector**

### Purpose
Semantic search across all court orders, judgments, and legal documents. Find similar cases or relevant precedents.

### Tech Stack
- **pgvector:** Vector embeddings stored in `vector_cache` table
- **Embedding model:** Sentence-transformers (`all-MiniLM-L6-v2`)
- **Search:** Cosine similarity on vector column

### Flow
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

---

## AIPOT-TRANSLATE 🟡 MEDIUM
**Multilingual legal translation EN/HI/PA**

### Purpose
Translate legal documents between English, Hindi, and Punjabi with high accuracy.

### Tech Stack
- **Model:** AI24x7 Meta MMS fine-tuned (or AI4Bharat IndicWav2Vec)
- **Output:** Preserved formatting (PDF/DOCX)

### Supported Languages
- English (en)
- Hindi (hi)
- Punjabi (pa)

### Accuracy Target
- Technical legal terms: 95%+ accuracy
- General content: 90%+ accuracy
- Confidence score stored in `translation_jobs.accuracy_score`

---

## Summary Table

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
