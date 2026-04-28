# GOOGLE CLOUD & GEMINI INTEGRATION PLAN — LETESE
**Version:** 1.0 | **Date:** 27 April 2026 | **For:** Arjun Singh / GOUP Consultancy Services LLP
**Status:** Ready to share with Google team

---

## 1. WHAT IS LETESE

LETESE is a full-stack Legal Practice Management SaaS for Indian advocates — think "Salesforce for lawyers." It runs case diaries, sends WhatsApp/SMS reminders, uses AI to draft petitions, scrapes court websites for updates, translates documents, generates GST invoices, and provides a collaborative document editor — all in one platform. Currently being built. Scale target: pan-India, 10,000–50,000 concurrent users initially, designed for 1 million users.

**Key differentiator:** 8 AI agents (called AIPOTs) that automate everything — court scraping, drafting, compliance checking, client communication, billing reminders, police-style system monitoring.

---

## 2. WHY GOOGLE CLOUD FOR LETESE

### Comparison: AWS vs Google Cloud vs Azure

| Criteria | AWS | Google Cloud | Azure |
|---|---|---|---|
| **AI/LLM leadership** | SageMaker, Bedrock | **Vertex AI, Gemini** ← strongest | Azure OpenAI |
| **Managed vector DB** | Aurora Vector DB | **Vertex AI Vector Search** | Azure AI Search |
| **Serverless containers** | ECS/Fargate | **Cloud Run** ← best auto-scale | Container Apps |
| **Legal/Compliance** | GovCloud (US only) | **Data residency in India** (asia-south1 Mumbai) | SOVerse |
| **Pricing** | Pay-per-use, complex | **Sustained use discounts auto** | Complicated |
| **Integration with GSuite** | GSuite connector possible | **Native** ← Google owns both | Weak |
| **LETESE fit score** | 7/10 | **9/10** | 6/10 |

**Recommendation: Google Cloud** because Gemini + Vertex AI + native GSuite integration = best fit for LETESE's AI-heavy, document-collaboration-forward architecture. Also GCP's Asia-South-1 (Mumbai) region gives India-local data residency.

---

## 3. GEMINI ENTERPRISE USE CASES — SPECIFIC & CONCRETE

### 3a. Legal Drafting (AIPOT-DRAFT replacement/enhancement)

**What:** Advocate pastes a plain-language case summary → Gemini produces a complete petition (Writ Petition, SLP, etc.) in formal legal English.

**How it works:**
```
Advocate types in Flutter app:
"Madhav Rao's house was demolished by municipality on 15 March 2025 without 
any notice. No opportunity to represent was given. This is violation of Article 14."

→ POST to LETESE API → /api/v1/drafts/generate
→ Gemini Ultra receives: case_summary + court_checklist_rules + previous_case_docs
→ Gemini Ultra context window: 2M tokens → can ingest full 50-page precedent judgment + 
  full court checklist + advocate's 20 previous petitions simultaneously
→ Returns: Complete formatted draft petition (not a skeleton)
→ Tiptap editor in Flutter shows draft in real-time
```

**API Pattern:**
```python
# Using Google Vertex AI
from vertexai.generative_models import GenerativeModel

model = GenerativeModel("gemini-2.0-pro")  # 2M token context

response = model.generate_content([
    {"role": "user", "parts": [f"""
    You are AIPOT-DRAFT, senior legal drafting assistant for Indian courts.
    Court: {court_display_name}
    Petition Type: {petition_type}
    Checklist Rules: {court_checklist_rules}
    Case Summary: {case_summary}
    Previous Case Context: {previous_petitions}
    Draft the complete petition in formal legal English. Number all paragraphs.
    Include: title page, synopsis, list of dates, facts, grounds, prayer, verification.
    """}
]})
```

**Volume:** ~500 drafts/day at 10K users → 2,500 drafts/day at 50K users.
**Gemini vs Qwen3-VL:** Use Qwen3-VL (free, on GPU server) for standard petitions (Simple CWP, routine consumer forum). Use Gemini Ultra for Supreme Court, complex constitutional writs, tax matters — where quality matters more than ₹0 cost.

---

### 3b. Email & Communication Triage (AIPOT-COMPLIANCE/COMMUNICATOR)

**What:** All client emails arrive via Gmail API → Gemini reads, classifies urgency, drafts replies, prioritizes inbox.

**Flow:**
```
Client emails: "I have not received court summons, what should I do?"
↓ Gmail API webhook (push notification)
↓ Gemini reads email + checks case context (case diary, order history)
↓ Gemini classifies: URGENCY=8/10, ACTION_REQUIRED=true, 
    Suggested reply: "Please share the case number so we can check. 
    If no summons received, we will file an urgency application."
↓ LETESE inbox: shows email with urgency badge + pre-drafted reply
↓ Advocate reviews → one-click send or edits
```

**API:** Gmail API + Gemini 2.0 Flash for speed (classification is fast, doesn't need Ultra)

---

### 3c. Google Calendar & Meet Integration

**What:** When AIPOT-SCRAPER detects a new court hearing → automatically create Google Calendar event + Google Meet link → send to advocate + client.

**Flow:**
```
Court website scraped: "Next hearing: 15 May 2025, 10:30 AM, Court 5, Division Bench"
↓ Kafka event: letese.diary.updates
↓ FastAPI: POST /api/v1/hearings (saves to DB)
↓ Google Calendar API: Create event
    {
      "summary": "HC Hearing: Sharma v. Union of India",
      "start": {"dateTime": "2025-05-15T10:30:00+05:30"},
      "end":   {"dateTime": "2025-05-15T11:30:00+05:30"},
      "conferenceData": {"createRequest": {"conferenceSolutionKey": {"type": "hangoutsMeet"}}},
      "attendees": [{"email": "advocate@lawfirm.in"}, {"email": "client@email.com"}]
    }
↓ Google Meet link generated automatically
↓ WhatsApp to client: "Your hearing is fixed for 15 May 2025 at 10:30 AM. Join via Meet: [link]"
```

**Google Calendar API scopes needed:**
- `https://www.googleapis.com/auth/calendar.events`
- OAuth2 consent (internal/workspace domain) or external with verification

---

### 3d. Document Intelligence (Replaces Tesseract OCR Pipeline)

**What:** Scanned PDFs of court orders (often poor quality, multi-column, Hindi/English mix) → Gemini PDF understanding → structured text extraction + meaning extraction.

**Current plan (without Google):**
- Tesseract OCR (local) → text extraction → spacy NER → store
- Problem: Tesseract fails on poor scans, multi-column, Gurmukhi script

**With Gemini (replaces Tesseract):**
```python
# Upload scanned PDF directly to Gemini
import vertexai
from vertexai.vision_models import ImageModel

model = ImageModel.from_pretrained("gemini-pro-vision")

# For PDFs: use multimodal capability
response = model.generate_content([
    Content(mime_type="application/pdf", data=pdf_bytes),
    """Extract and return:
    1. Full text of this court order (preserve structure)
    2. Next hearing date and time
    3. Names of parties (petitioner and respondent)
    4. Key directions to parties
    5. Any interim relief granted
    Format as structured JSON."""
])
```

**Accuracy gain:** Tesseract ~60% on bad scans → Gemini ~95%. This alone saves huge manual review effort.

---

### 3e. RAG on SC + 25 HC Judgments (Vertex AI Vector Search)

**What:** Store all Supreme Court + High Court judgments as vectors → advocate searches by natural language → Gemini grounds answers in actual case law.

**Architecture:**
```
Judgments corpus: ~5 million judgments (SC + all 25 HCs)
↓ ETL pipeline: chunk at 512 tokens, overlap 64 tokens
↓ Embed with text-embedding-004 (Google's embedding model)
↓ Store in Vertex AI Vector Search index (serverless, scales to billions)
↓ Advocate query: "Section 144 IPC preventive detention cases where 
                    Article 21 violation alleged"
↓ Retrieve top-5 similar chunks from vector index
↓ Gemini Ultra receives: retrieved_chunks + query
↓ Gemini answers with citations: "In [Case Citation] the Supreme Court held..."
```

**Contrast with pgvector:**
| | pgvector (current plan) | Vertex AI Vector Search |
|---|---|---|
| Max vectors | ~10 million | 2 billion |
| Setup | Manual on PostgreSQL | Fully managed, serverless |
| Cost | ~₹20K/month (infra) | ~₹1.5L/month (at scale) |
| Gemini integration | Indirect | Native (same GCP) |
| Maintenance | High | Zero |
| **Verdict** | Good for MVP | Essential at 1M users |

**Recommendation:** pgvector for MVP (10K users). Migrate to Vertex AI Vector Search at 100K+ users.

---

### 3f. Google Agentic AI (Gemini Agentic / Agent Development Kit)

**This is the most exciting use case.** Google Agentic AI allows building agents that:

**Agent 1 — Court Monitor Agent:**
```
Trigger: Every morning at 6 AM
Action: 
  1. Read list of all active cases (from LETESE DB)
  2. For each case → query court website via scraper
  3. If new order detected:
     - Extract order text (Gemini for PDF understanding)
     - Determine if any party action required
     - Create task in LETESE
     - Send WhatsApp alert to advocate
     - Update Google Calendar if new hearing found
  4. Report: "Monitored 847 cases. 12 new orders found. 3 hearings updated."
```

**Agent 2 — Compliance Review Agent:**
```
Trigger: When advocate clicks "Check Compliance"
Action:
  1. Load court checklist for {court_code, petition_type}
  2. Read drafted petition
  3. Gemini Ultra: analyze each checklist rule against document
  4. Return: red-lined checklist showing exactly what's missing
  5. Generate suggested fixes for each failed check
```

**Agent 3 — Invoice Generation Agent:**
```
Trigger: When case milestone reached OR manual trigger
Action:
  1. Read case activity log (from MongoDB): hearings attended, drafts filed, orders analyzed
  2. Gemini: draft professional invoice description based on activity
  3. Create invoice in LETESE (via API)
  4. Generate PDF
  5. Send WhatsApp to client with payment link
```

**API access needed:** Google Agent Development Kit (request from Google team — may be in private preview)

---

### 3g. Google Drive Auto-Backup (Per Tenant)

**What:** Every document created/uploaded in LETESE automatically synced to that firm's private Google Drive.

**Drive Structure per firm:**
```
/LETESE (root folder, shared with firm)
  /Cases
    /CWP-1234-2024 Sharma v UOI
      /01-Petitions
        - Writ_Petition_v1.docx
        - Writ_Petition_v2.docx
      /02-Orders
        - Order_15Mar2025.pdf
      /03-Invoices
        - INV-2025-0001.pdf
      /04-Translations
        - Punjabi_Order_Translated.pdf
    /CWP-5678-2024
  /Firm_Documents
    - Standard_Vakalatnama.docx
    - Court_Fee_Calculator.xlsx
```

**API:** Google Drive API v3
- Create folder structure on first tenant onboarding
- Use `drive.file` scope (app-only access, no broad file permissions)
- Watch API (push notifications) for real-time sync

---

### 3h. Google Sheets Billing Dashboard

**What:** Advocate wants invoice/billing data in Google Sheets, not just LETESE dashboard.

**Flow:**
```
Invoice created in LETESE
↓ POST to Google Sheets API
↓ Row appended to firm's "Billing" sheet:
  Date | Client | Case | Amount | GST | Total | Status | Payment Link
↓ Firm owner gets email: "New invoice ₹45,000 added to LETESE Billing Sheet"
```

**Also:** LETESE analytics pushed to Google Sheets for advocates who prefer spreadsheets.

---

### 3i. Grounding with Google Search (For Legal Research)

**What:** When advocate asks research question → Gemini with Google Search grounding → gets latest judgments + news.

```
Advocate: "What is the latest position on Section 21(6) of the IBC regarding
           personal guarantors after the 2024 Supreme Court judgment?"

↓ Gemini with Google Search tool
↓ Returns: "The Supreme Court in [Citation, Date] held that... 
            This was further clarified in [2025]..."
↓ Includes actual links to judgments
↓ Stored as "Research Query" in case file
```

---

## 4. GOOGLE CLOUD SERVICES — FULL STACK RECOMMENDATION

### Compute & Containers

| Service | Use in LETESE | Config | Monthly Cost (est.) |
|---|---|---|---|
| **Cloud Run** (primary) | FastAPI backend, AIPOT agents, document processor | 2 vCPU, 4GB RAM, min 1 instance | ₹45K-₹1.5L depending on traffic |
| **GKE Autopilot** (backup) | Kafka broker, Redis (if not Memorystore) | 3-5 node cluster | ₹80K-₹2L |
| **Compute Engine** | GPU workloads beyond current server | n1-standard-8 + T4 GPU | ₹60K (pay-per-use) |

**Recommendation:** Start with Cloud Run for stateless services (API, AIPOTs). Keep Kafka + Redis on bare metal (existing server) for now. Migrate to Cloud Run fully once MVP is stable.

### Database Layer

| Service | Use | Config | Monthly Cost (est.) |
|---|---|---|---|
| **Cloud SQL PostgreSQL 16** | Primary DB (replace 187.127.139.147:5433) | db-n1-highmem-8, 100GB SSD, HA | ₹65K |
| **Cloud SQL read replica** | Analytics queries | db-n1-standard-4 | ₹25K |
| **Spanner** (evaluate later) | Only if truly global, 1M+ users | Start with 100 RUs | ₹1.5L+ |
| **Memorystore Redis** | Cache, sessions (replace self-hosted Redis) | 4GB, HA mode | ₹12K |
| **Cloud Storage (GCS)** | Documents, PDFs, voice files | Standard, lifecycle policies | ₹5K (at MVP scale) |

### AI & Analytics

| Service | Use | Config | Monthly Cost (est.) |
|---|---|---|---|
| **Vertex AI** | Gemini Ultra/Flash API | Pay-per-token | ₹50K-₹5L (volume dependent) |
| **Vertex AI Vector Search** | Judgment RAG | Serverless index | ₹30K-₹2L |
| **BigQuery** | Analytics, billing analysis | On-demand | ₹5K-₹20K |
| **Looker Studio** | BI dashboards (replace Grafana for business) | Included with GCP | Free |

### Networking & Security

| Service | Use | Config | Monthly Cost (est.) |
|---|---|---|---|
| **Cloud CDN** | Flutter app static assets, API caching | Global | ₹8K |
| **Cloud Armor** | WAF, DDoS protection | Standard rule set | ₹5K |
| **Cloud Load Balancing** | Global HTTP(S) LB | Included with CDN | ₹3K |
| **Static IP** | Reserved IP for LETESE API | 1 static regional | ₹300 |
| **Cloud VPN** | Connect LETESE GPU server to GCP | Cloud Router | ₹2K |

### Management

| Service | Use | Config | Monthly Cost (est.) |
|---|---|---|---|
| **Cloud Monitoring** | API + infrastructure | Included | Free |
| **Cloud Logging** | Centralized logs | 30-day retention | ₹3K |
| **Secret Manager** | API keys, JWT secrets | Included | Free |
| **API Gateway / Apigee** | API management, rate limiting | Apigee X | ₹20K |

### Recommended: Premium Support (₹1.5L/year)

At 50K users and AI-critical product: Premium support with TAM (Technical Account Manager) is worth it.

---

## 5. INTEGRATION WITH EXISTING GPU SERVER (43.242.224.231)

| Workload | Where | Why |
|---|---|---|
| Court scraping (Playwright) | Keep on GPU server | Already running, no GCP needed |
| Standard petition drafts (Qwen3-VL) | Keep on GPU server | ₹0 cost, good enough for 80% |
| Complex SC/HC petitions | Gemini Ultra on GCP | Best quality, worth the cost |
| Judgment RAG vectors | pgvector on GPU server (MVP) → Vertex AI (scale) | pgvector fine at 10K users |
| Document translation (Indic) | Keep IndicTrans2 on Mac Mini M4 or GPU server | Better than Gemini for Indic scripts |
| Real-time PDF OCR | Replace with Gemini Vision | Much better accuracy |

**Split recommendation:**
```
Budget approach (MVP):     GPU server handles 80% of AI, Gemini handles 20%
Premium approach (Scale):  GCP handles everything AI, GPU server retired
```

**API gateway at GPU server:**
```
                    ┌─────────────────┐
Advocate Request → │ GPU Server :8080 │ → Qwen3-VL (free, fast)
                    └────────┬────────┘
                             │ (if complex task)
                             ↓
                    ┌─────────────────┐
                    │ Vertex AI Gemini │ (paid, best quality)
                    │ on Google Cloud  │
                    └─────────────────┘
```

---

## 6. SCALING: 200 → 50,000 CONCURRENT USERS

### What works at 200 users (current design)
- Single PostgreSQL server (187.127.139.147:5433)
- Single FastAPI server on port 4007
- Self-managed Redis
- Local Kafka (single broker)

### What breaks at 10,000 users
- Single DB connection pool saturates
- No CDN → slow Flutter app loading
- No auto-scaling → server crashes at peak
- Single-region latency (North India advocates vs Mumbai GCP)

### What breaks at 50,000 users
- PostgreSQL single-region insufficient
- Kafka single broker inadequate
- No disaster recovery (no DB replication)
- Security: no WAF, no DDoS protection

### Architecture at 50,000 users:
```
                         ┌─ Cloud CDN (Mumbai) ───────────────────────┐
Advocates ──Internet───→│  Flutter Web App (static, cached)           │
                         └───────────────────────────────────────────┘
                                           │
                         ┌─ Cloud Armor (WAF/DDoS) ──────────────────┐
                         │  Rate limiting: 100 req/min per user       │
                         │  Bot protection, SQL injection, etc.       │
                         └───────────────────────────────────────────┘
                                           │
                         ┌─ Cloud Load Balancer (Global HTTP(S)) ──┐
                         │  SSL termination, routing                 │
                         └───────────────────────────────────────────┘
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              │          Cloud Run (auto-scales 1→100 instances)       │
              │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
              │  │ FastAPI  │  │ AIPOT    │  │ AIPOT    │  ...          │
              │  │ Backend  │  │ Scraper  │  │ Draft    │               │
              │  └──────────┘  └──────────┘  └──────────┘               │
              └────────────────────────────┼────────────────────────────┘
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              │  Data Layer                  │                           │
              │  ┌──────────┐  ┌──────────┐ │  ┌──────────────────────┐│
              │  │Cloud SQL │  │Memorystore│ │  │  Apache Kafka         ││
              │  │PostgreSQL│  │  Redis   │ │  │  (3 brokers, 30 part.) ││
              │  │ + read   │  │  (cache) │ │  │  43.242.224.231:9092  ││
              │  │ replicas │  │          │ │  └──────────────────────┘│
              │  └──────────┘  └──────────┘ │                            │
              │                            │  ┌──────────────────────┐ │
              │                            │  │ Vertex AI / Gemini  │ │
              └────────────────────────────┘  │  (Google Cloud)      │ │
                                             └──────────────────────┘ │
                                                                       │
                                          ┌────────────────────────────┘
                                          │  Storage
                                          │  ┌──────────────────────────┐
                                          │  │ Google Cloud Storage (GCS)│
                                          │  │ /cases /invoices /drafts  │
                                          │  └──────────────────────────┘
                                          │
                                          │  ┌──────────────────────────┐
                                          │  │ Vertex AI Vector Search  │
                                          │  │ (5M judgment embeddings)  │
                                          │  └──────────────────────────┘
```

### Load Testing Plan
- Use Locust (already planned in blueprint) with 50K virtual users
- Test: 500 concurrent WebSocket diary connections
- Target: P99 latency < 500ms
- Nightly run in CI/CD pipeline

---

## 7. G SUITE INTEGRATION (Google Workspace)

### Per Advocate Firm Setup
```
Onboarding flow:
1. Advocate signs up on LETESE with Google OAuth (existing plan)
2. If firm has Google Workspace (law firm domain):
   → Request Google Drive + Calendar + Sheets scope
   → Create /LETESE folder in firm's Google Drive
   → Link Google Calendar (read/write events)
3. If no Google Workspace:
   → Use LETESE's own calendar + storage
   → No Google Drive integration
```

### OAuth Scopes Required
```python
SCOPES = [
    "openid",                          # Authentication
    "email",                           # User email
    "profile",                         # User profile
    # Gmail
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    # Drive
    "https://www.googleapis.com/auth/drive.file",      # App-created files only
    "https://www.googleapis.com/auth/drive.readonly",  # Read firm docs
    # Calendar
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly",
    # Sheets
    "https://www.googleapis.com/auth/spreadsheets",
    # Meet
    "https://www.googleapis.com/auth/meetings.space.created",
]
```

### Security Model
- Each tenant (law firm) = separate OAuth tokens, stored encrypted in Cloud SQL
- LETESE NEVER has full Drive access — only app-created folders
- Tenant isolation enforced at OAuth token level
- Advocate can revoke LETESE access anytime from Google Account settings

---

## 8. BUDGET ESTIMATES (Rough, GCP asia-south1 Mumbai)

### Scenario A: 10,000 Monthly Active Users
| Component | Monthly |
|---|---|
| Cloud Run (API + AIPOTs) | ₹60,000 |
| Cloud SQL PostgreSQL HA | ₹65,000 |
| Memorystore Redis | ₹12,000 |
| Cloud Storage (GCS) | ₹5,000 |
| Vertex AI (Gemini Flash) | ₹40,000 |
| Cloud CDN + Armor + LB | ₹16,000 |
| BigQuery + Looker | ₹8,000 |
| API Gateway | ₹20,000 |
| **Total** | **₹2,26,000/month (~₹27L/year)** |

### Scenario B: 50,000 Monthly Active Users
| Component | Monthly |
|---|---|
| Cloud Run (scaled) | ₹1,50,000 |
| Cloud SQL + read replica | ₹90,000 |
| Memorystore Redis HA | ₹25,000 |
| Cloud Storage | ₹15,000 |
| Vertex AI (Gemini Ultra + Flash) | ₹2,00,000 |
| Vertex AI Vector Search | ₹60,000 |
| Cloud CDN + Armor + LB | ₹30,000 |
| BigQuery + Looker | ₹20,000 |
| Premium Support + TAM | ₹1,25,000 |
| **Total** | **₹7,15,000/month (~₹86L/year)** |

### Compare: Self-hosted (current GPU server approach)
- Electricity + bandwidth: ~₹15K/month
- But: no scalability, no managed services, no support
- At 10K users, self-hosted becomes unstable

**Note from Arjun: "Budget is NOT an issue"** — so GCP is absolutely the right call.

---

## 9. WHAT WE NEED FROM GOOGLE TEAM — THE EXACT LIST

**Share this section directly with your Google contact:**

### 9a. GCP Project Setup
- [ ] GCP Project ID and Number (create new project: `letese-production`)
- [ ] Billing account ID linked
- [ ] Confirm region: `asia-south1` (Mumbai) for India data residency

### 9b. Service Account (for LETESE backend)
- [ ] Create service account: `letese-backend@letese-production.iam.gserviceaccount.com`
- [ ] Grant these IAM roles:
  - `roles/run.admin` (Cloud Run management)
  - `roles/cloudsql.client` (Cloud SQL access)
  - `roles/storage.objectAdmin` (GCS read/write)
  - `roles/aiplatform.user` (Vertex AI)
  - `roles/bigquery.dataEditor` (BigQuery)
  - `roles/logging.logWriter` (Cloud Logging)
  - `roles/monitoring.metricWriter` (Cloud Monitoring)
  - `roles/secretmanager.secretAccessor` (Secret Manager)
- [ ] Download JSON key file (securely share with LETESE tech team)

### 9c. Google Workspace (G Suite) — Domain-Wide Delegation
**If advocates use Google Workspace (law firm has company Google account):**

- [ ] Enable Gmail API for the Google Workspace domain
- [ ] Authorize LETESE app for Gmail scopes (see SCOPES list above)
- [ ] Authorize Google Drive API scopes for domain
- [ ] Authorize Google Calendar API scopes for domain
- [ ] Authorize Google Sheets API scopes for domain
- [ ] OAuth2 consent screen: Internal (for workspace) or External with verification
- [ ] Publish OAuth app (if external, needs Google verification — takes 2-4 weeks)

**If advocates use personal Gmail:**
- [ ] No domain-wide delegation needed
- [ ] Individual OAuth flow per user (standard, no admin approval)

### 9d. Vertex AI API
- [ ] Enable Vertex AI API on the project
- [ ] Request quota increase: 1000 requests/minute (for production)
- [ ] Access to: `gemini-2.0-pro`, `gemini-2.0-flash`, `gemini-2.0-ultra` (if available)
- [ ] Agent Development Kit access (if available in preview)
- [ ] text-embedding-004 model access

### 9e. Google Cloud Search API
- [ ] Enable Cloud Search API
- [ ] Configure for RAG use case
- [ ] Data connector for judgment corpus

### 9f. Google Drive / Calendar / Sheets APIs
- [ ] All already covered under domain-wide delegation above

### 9g. Networking
- [ ] Reserve 1 static external IP in asia-south1
- [ ] Firewall rules: allow LETESE GPU server (43.242.224.231) to connect to Cloud SQL
- [ ] Consider Cloud VPN between GPU server and GCP for secure DB connection

### 9h. GCP Support
- [ ] Current: Basic (free)
- [ ] Recommended: **Production Support** (₹1.15L/year) or **Premium** (₹6L/year)
  - Production: 4-hour response, business hours
  - Premium: 15-min response, 24/7, TAM included
- [ ] Request Technical Account Manager (TAM) for LETESE account

### 9i. Google Agentic AI / Agent Development Kit
- [ ] Ask Google team directly: Is Agent Development Kit available?
- [ ] If yes: Request access (may be in private preview)
- [ ] Use case: Court monitoring agent, compliance agent, invoice agent

---

## 10. QUESTIONS TO ASK GOOGLE TEAM

Ask these directly — write down the answers:

### Pricing & Commercial
1. **Gemini Enterprise pricing:** Is it per-token, per-user, or flat monthly? What's the volume discount at 10M+ tokens/month?
2. **Vertex AI Vector Search pricing:** Is it per-query or per-vector-stored? At 5M vectors + 10K queries/day, what's the monthly cost?
3. **Cloud Run at scale:** At 50K concurrent users, how many Cloud Run instances? Is there a ceiling on auto-scaling?
4. **GCP promo credits:** Does Google have startup/partner credits we can apply?

### Technical
5. **Data residency guarantee:** Does Google guarantee in writing that all data stays in India (asia-south1)? For legal privilege documents, we need this assurance.
6. **Client-side encryption:** For extremely sensitive legal documents (e.g., criminal matters, corporate litigation), can we use CMEK (customer-managed encryption keys)? Does this conflict with Gemini grounding?
7. **Agent Development Kit:** Is it available? What's the pricing model? Can it be used for autonomous agents that take actions (not just answer questions)?
8. **RAG + Gemini grounding:** With Vertex AI Vector Search + Gemini grounding, what's the P99 latency for a typical legal research query (5 retrieved chunks, 2000-token response)?
9. **Gmail API rate limits:** What's the sending limit for transactional emails via Gmail API? We're sending 50K-200K WhatsApp/email notifications/day.
10. **Google Drive API:** For 50K users each with 1GB Drive storage, does Google have an enterprise Drive agreement?

### Partnership
11. **Google for Startups Cloud Program:** Are we eligible? Can we get up to ₹10L in GCP credits?
12. **Google Cloud Partner status:** Can GOUP Consultancy become a Google Cloud partner? This could help other clients too.
13. **Joint go-to-market:** Would Google co-market LETESE to their enterprise legal clients in India?

---

## 11. MIGRATION PATH

### Phase 1 — Parallel Run (Weeks 1-4)
**Keep existing infrastructure. Add Google Cloud for AI only.**
- Enable Vertex AI, get Gemini API keys
- Keep PostgreSQL, Redis, Kafka on existing server (187.127.139.147)
- Keep Qwen3-VL on GPU server (43.242.224.231) for standard tasks
- Use Gemini Ultra for complex SC/HC petitions (paid, best quality)
- Set up GCS bucket as primary document storage (parallel to local)
- Set up Cloud Logging + Monitoring (replace Grafana for business metrics)
- **Deliverable:** First advocates can log in, create cases, get AI drafts

### Phase 2 — Managed Services Migration (Weeks 5-8)
**Move from bare metal to GCP managed services.**
- Migrate PostgreSQL → Cloud SQL (use Cloud SQL Auth Proxy, zero downtime)
- Migrate Redis → Memorystore
- Migrate GCS bucket as primary document storage
- Set up Cloud Run for API server (containerize FastAPI)
- Keep Kafka on bare metal (Cloud Run for Kafka producer/consumer services)
- Enable Cloud CDN + Cloud Armor
- **Deliverable:** Production-ready, auto-scaling, secure

### Phase 3 — Full Scale (Months 3-6)
**Scale to 10K-50K users.**
- Vertex AI Vector Search for judgment RAG
- BigQuery for analytics
- Looker for business dashboards
- GKE Autopilot if Cloud Run limits hit
- Disaster recovery setup: cross-region replication
- Load test at 50K concurrent users
- **Deliverable:** Can handle 50K concurrent, globally distributed

### Phase 4 — AI Excellence (Ongoing)
**Let AI do more of the work.**
- Deploy Gemini Agentic agents (Court Monitor, Compliance, Invoice)
- Full Google Workspace integration (Drive, Calendar, Sheets, Meet)
- Auto-backup all documents to firm Google Drive
- Post-judgment analysis fully automated
- **Deliverable:** Most automated legal SaaS in India

---

## 12. ONE-PAGE SUMMARY (For Your WhatsApp to Google Contact)

```
LETESE — Legal Practice Management SaaS for Indian advocates
Scale: 10K users now → 1M users eventually
Budget: No constraint

What we need from Google:
1. GCP project setup (asia-south1/Mumbai)
2. Service account with Vertex AI + Cloud SQL + GCS roles
3. Gemini API (Ultra + Flash) with 1000 req/min quota
4. Google Workspace domain-wide delegation (Gmail + Drive + Calendar + Sheets)
5. Agent Development Kit access (autonomous agents for court monitoring)
6. Cloud Search API for legal RAG on 5M judgments
7. Premium support with TAM
8. Partner program / startup credits if available

What we bring:
- Guaranteed 10K-50K users in Year 1 (legal market in India)
- Integration with existing GPU server (43.242.224.231) — hybrid approach
- LETESE brand growing fast in Indian legal tech space
- Opportunity to showcase Gemini in legal domain (India-wide)
```

---

*Document prepared for Arjun Singh | GOUP Consultancy Services LLP*
*Questions? Ask your Google contact or ask LETESE tech team*

---

## 13. GOOGLE API CREDENTIALS CHECKLIST (Send This to Google Contact)

```
═══════════════════════════════════════════════════════════════
TO: Google Cloud Team (India)
FROM: Arjun Singh, GOUP Consultancy Services LLP
RE: LETESE — AI-Powered Legal SaaS — API & Integration Requirements
═══════════════════════════════════════════════════════════════

PROJECT OVERVIEW:
LETESE is India's most comprehensive Legal Practice Management SaaS.
Target: 10,000-50,000 advocates in Year 1, pan-India.
Budget: NO CONSTRAINT. Quality matters.

─────────────────────────────────────────────────
SECTION A: GCP PROJECT SETUP
─────────────────────────────────────────────────
□ GCP Project Name: [letese-production] — please create
□ Billing Account: [Please link]
□ Region: asia-south1 (Mumbai) ONLY — India data residency required
□ Enable these APIs:
  - Vertex AI API
  - Cloud Run API
  - Cloud SQL Admin API
  - Cloud Storage API
  - BigQuery API
  - Cloud Memorystore API
  - Secret Manager API
  - Cloud Logging API
  - Cloud Monitoring API
  - Compute Engine API
  - Cloud DNS API
  - Cloud Armor API
  - Cloud CDN API
  - Apigee API (or API Gateway)

─────────────────────────────────────────────────
SECTION B: SERVICE ACCOUNT (For LETESE Backend)
─────────────────────────────────────────────────
□ Create: letese-backend@[PROJECT].iam.gserviceaccount.com
□ Download JSON key — share securely with LETESE tech team
□ IAM Roles to grant:
  • roles/aiplatform.user          (use Vertex AI)
  • roles/run.admin                (manage Cloud Run)
  • roles/cloudsql.client          (connect to Cloud SQL)
  • roles/cloudsql.instanceUser   (Cloud SQL users)
  • roles/storage.objectAdmin      (read/write GCS buckets)
  • roles/bigquery.dataEditor     (write analytics data)
  • roles/bigquery.jobUser        (run queries)
  • roles/logging.logWriter       (write logs)
  • roles/monitoring.metricWriter  (write metrics)
  • roles/monitoring.alertManager (create alerts)
  • roles/secretmanager.secretAccessor (read secrets)

─────────────────────────────────────────────────
SECTION C: VERTEX AI / GEMINI
─────────────────────────────────────────────────
□ Enable Vertex AI API on project
□ Enable these models:
  • gemini-2.0-pro         (2M token context, complex petitions)
  • gemini-2.0-flash      (fast, email triage, classification)
  • gemini-2.0-ultra      (best quality, if available)
  • text-embedding-004     (for RAG vector search)
□ Request quota: 1,000 requests/minute (production volume)
□ REGION: asia-south1 ONLY
□ Ask: Is Agent Development Kit available? We want autonomous agents
□ Ask: Cloud Search API — for legal RAG (5M Supreme Court + HC judgments)

─────────────────────────────────────────────────
SECTION D: GOOGLE WORKSPACE (G SUITE) — DOMAIN-WIDE DELEGATION
─────────────────────────────────────────────────
[Only if law firms have Google Workspace / company email]

□ Gmail API — authorize for domain:
  Scopes needed:
  • https://www.googleapis.com/auth/gmail.send        (send emails)
  • https://www.googleapis.com/auth/gmail.readonly     (read incoming)

□ Google Drive API — authorize for domain:
  Scopes needed:
  • https://www.googleapis.com/auth/drive.file         (create app folders)
  • https://www.googleapis.com/auth/drive.readonly    (read firm documents)

□ Google Calendar API — authorize for domain:
  Scopes needed:
  • https://www.googleapis.com/auth/calendar.events   (create hearings)
  • https://www.googleapis.com/auth/calendar.readonly

□ Google Sheets API — authorize for domain:
  Scope needed:
  • https://www.googleapis.com/auth/spreadsheets      (billing dashboards)

□ Google Meet API — authorize for domain:
  Scope needed:
  • https://www.googleapis.com/auth/meetings.space.created (create Meet links)

□ OAuth2 Consent Screen:
  • Internal (recommended): Only workspace users can authorize
  • If external: Needs Google verification (takes 2-4 weeks)

─────────────────────────────────────────────────
SECTION E: GOOGLE DRIVE SETUP (Auto-Backup)
─────────────────────────────────────────────────
□ Create demo Google Workspace org to test
□ LETESE needs: drive.file scope (NOT drive or drive.readonly)
  [Only LETESE-created files, no access to firm's existing files]
□ Verify: Advocate can revoke LETESE access from myaccount.google.com

─────────────────────────────────────────────────
SECTION F: NETWORKING
─────────────────────────────────────────────────
□ Reserve 1 static external IP in asia-south1
□ Firewall: Allow LETESE GPU server (43.242.224.231) → Cloud SQL
□ Consider: Cloud VPN between GPU server and GCP VPC
□ SSL: Managed SSL certificates via Cloud CDN (free)

─────────────────────────────────────────────────
SECTION G: SUPPORT & PARTNERSHIP
─────────────────────────────────────────────────
□ Upgrade to: Production Support (₹1.15L/year) or Premium (₹6L/year)
□ Request: Technical Account Manager (TAM) for LETESE account
□ Ask: Google for Startups Cloud Program — are we eligible?
□ Ask: Google Cloud Partner status for GOUP Consultancy
□ Ask: Joint go-to-market opportunity (Google co-marketing in India)

─────────────────────────────────────────────────
SECTION H: QUESTIONS FOR GOOGLE TEAM
─────────────────────────────────────────────────
1. Gemini Enterprise pricing model? (per-token or flat monthly?)
2. Vertex AI Vector Search cost at 5M vectors + 10K queries/day?
3. Data residency guarantee — written assurance for legal privilege data?
4. Client-side encryption (CMEK) — available? Does it block Gemini grounding?
5. Agent Development Kit — available? Pricing?
6. RAG latency — P99 for legal research query (5 chunks + 2000-token answer)?
7. GCP promo credits for legal tech startup?
8. Is there a Google Cloud legal industry team in India we can meet?
