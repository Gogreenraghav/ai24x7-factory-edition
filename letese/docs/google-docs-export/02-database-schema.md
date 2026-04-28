# LETESE — Database Schema (PostgreSQL)

## Overview
- **Database:** PostgreSQL (ai_drafting DB) at `187.127.139.147:5433`
- **Extensions:** pgvector enabled ✅ (for legal research AI)
- **Multi-tenant:** Row-Level Security (RLS) enforced
- **Total existing tables:** 21 tables
- **ORM:** SQLAlchemy 2.0 (async)

---

## Existing Tables (21 tables — REUSE & FIX)

### 1. advocates
Law firm / advocate account — **MAIN USER TABLE**

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | Unique identifier |
| tenant_id | UUID | FK → tenants.id, NOT NULL | Multi-tenant isolation |
| name | VARCHAR(255) | NOT NULL | Full name |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Login email |
| phone | VARCHAR(20) | UNIQUE, NOT NULL | WhatsApp number |
| password_hash | VARCHAR(255) | NOT NULL | Hashed password |
| bar_council_no | VARCHAR(100) | NULL | Bar Council Registration No. |
| firm_name | VARCHAR(255) | NULL | Law firm name |
| role | ENUM | DEFAULT 'advocate' | advocate, clerk, paralegal, intern |
| plan | ENUM | DEFAULT 'basic' | basic, professional, elite, enterprise |
| is_verified_email | BOOLEAN | DEFAULT FALSE | Email OTP verified |
| is_verified_phone | BOOLEAN | DEFAULT FALSE | WhatsApp OTP verified |
| avatar_url | VARCHAR(500) | NULL | Profile picture |
| address | TEXT | NULL | Office address |
| experience_years | INTEGER | NULL | Years of practice |
| specialization | VARCHAR(255)[] | NULL | Areas of law |
| plan_started_at | TIMESTAMP | NULL | Subscription start |
| plan_expires_at | TIMESTAMP | NULL | Subscription expiry |
| storage_used_bytes | BIGINT | DEFAULT 0 | Storage consumed |
| storage_limit_bytes | BIGINT | DEFAULT 5368709120 | 5GB for Basic |
| case_count | INTEGER | DEFAULT 0 | Cases created |
| case_limit | INTEGER | DEFAULT 30 | Based on plan |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |
| is_active | BOOLEAN | DEFAULT TRUE | Soft delete |

**Indexes:** email, tenant_id, role

---

### 2. clients
End clients of advocates

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| advocate_id | UUID | FK → advocates.id, NOT NULL | Primary advocate |
| name | VARCHAR(255) | NOT NULL | Client full name |
| phone | VARCHAR(20) | NOT NULL | Primary phone |
| alt_phone | VARCHAR(20) | NULL | Alternate phone |
| email | VARCHAR(255) | NULL | |
| address | TEXT | NULL | |
| occupation | VARCHAR(255) | NULL | |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |
| is_active | BOOLEAN | DEFAULT TRUE | |

**Indexes:** advocate_id, tenant_id

---

### 3. cases
Court cases — **CORE TABLE**

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| client_id | UUID | FK → clients.id, NOT NULL | |
| advocate_id | UUID | FK → advocates.id, NOT NULL | Assigned advocate |
| case_no | VARCHAR(100) | NULL | Court case number (CNR) |
| cnlr_format | VARCHAR(50) | NULL | CNR number (P&H HC format: CRM-M-YYYY-NNNNN) |
| court_name | VARCHAR(255) | NOT NULL | e.g., "Punjab & Haryana High Court" |
| court_code | VARCHAR(50) | NULL | e.g., "phhc", "sci", "delhihc" |
| case_type | VARCHAR(100) | NOT NULL | CWP, CRM, CRP, Writ, Suit, SLP, Consumer |
| subject | VARCHAR(500) | NULL | Case subject/title |
| status | ENUM | DEFAULT 'active' | active, disposed, dismissed, transferred, pending |
| priority | ENUM | DEFAULT 'normal' | low, normal, high, urgent |
| next_hearing_date | DATE | NULL | Next hearing date |
| last_hearing_date | DATE | NULL | Previous hearing |
| stage | VARCHAR(100) | NULL | Current case stage |
| description | TEXT | NULL | Case notes |
| opposing_party | VARCHAR(255) | NULL | Opposing party name |
| opposing_counsel | VARCHAR(255) | NULL | Opposing lawyer |
| case_data | JSONB | DEFAULT '{}' | Flexible metadata |
| filing_date | DATE | NULL | When case was filed |
| disposal_date | DATE | NULL | When disposed |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |
| is_active | BOOLEAN | DEFAULT TRUE | |

**Indexes:** advocate_id, client_id, status, next_hearing_date, tenant_id, court_code

---

### 4. documents
Case document vault

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| case_id | UUID | FK → cases.id, NOT NULL | |
| uploaded_by | UUID | FK → advocates.id, NOT NULL | Who uploaded |
| name | VARCHAR(255) | NOT NULL | Display name |
| file_name | VARCHAR(255) | NOT NULL | Original filename |
| file_url | VARCHAR(500) | NOT NULL | S3/storage URL |
| s3_key | VARCHAR(500) | NOT NULL | S3 object key |
| doc_type | VARCHAR(100) | NOT NULL | petition, order, judgment, evidence, correspondence, other |
| mime_type | VARCHAR(100) | NULL | PDF, JPG, PNG, DOCX |
| file_size_bytes | BIGINT | NULL | Size in bytes |
| page_count | INTEGER | NULL | For PDFs |
| tags | VARCHAR(255)[] | DEFAULT '{}' | Searchable tags |
| is_ai_generated | BOOLEAN | DEFAULT FALSE | AI drafted document |
| draft_id | UUID | FK → drafts.id, NULL | Link to AI draft if applicable |
| verified_by | UUID | FK → advocates.id, NULL | Who verified |
| verified_at | TIMESTAMP | NULL | When verified |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |
| is_active | BOOLEAN | DEFAULT TRUE | |

**Indexes:** case_id, uploaded_by, doc_type, tenant_id

---

### 5. drafts
AI-generated petition drafts

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| case_id | UUID | FK → cases.id, NULL | Optional case link |
| advocate_id | UUID | FK → advocates.id, NOT NULL | Who requested |
| draft_type | VARCHAR(100) | NOT NULL | CWP, CRM, CRP, Writ, Suit, SLP, Consumer Complaint |
| title | VARCHAR(255) | NOT NULL | Draft title |
| content | TEXT | NOT NULL | AI-generated content |
| prompt_used | TEXT | NULL | Original prompt for reproducibility |
| version | INTEGER | DEFAULT 1 | Version number |
| status | ENUM | DEFAULT 'generated' | draft, approved, filed, rejected |
| ai_model | VARCHAR(100) | DEFAULT 'ai24x7-qwen3-vl' | Model used |
| compliance_score | DECIMAL(5,2) | NULL | AIPOT-COMPLIANCE score (0-100) |
| compliance_report | JSONB | DEFAULT '{}' | Detailed compliance check results |
| approved_by | UUID | FK → advocates.id, NULL | Who approved |
| approved_at | TIMESTAMP | NULL | When approved |
| filed_court | VARCHAR(255) | NULL | Court where filed |
| filed_date | DATE | NULL | Filing date |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |
| is_active | BOOLEAN | DEFAULT TRUE | |

**Indexes:** case_id, advocate_id, draft_type, status, tenant_id

---

### 6. court_orders
Scraped court orders (from AIPOT-SCRAPER)

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| case_id | UUID | FK → cases.id, NULL | Linked case (by CNR matching) |
| court_name | VARCHAR(255) | NOT NULL | Source court |
| court_code | VARCHAR(50) | NOT NULL | e.g., "phhc", "sci" |
| case_no | VARCHAR(100) | NOT NULL | Case number |
| cnlr_format | VARCHAR(50) | NULL | CNR if available |
| order_date | DATE | NOT NULL | Date of order |
| order_text | TEXT | NOT NULL | Full order content |
| order_summary | TEXT | NULL | AI-generated summary |
| order_type | VARCHAR(100) | NULL |interim, final, interlocutory, order_sheet |
| order_hash | VARCHAR(64) | UNIQUE | SHA256 for deduplication |
| scraped_at | TIMESTAMP | DEFAULT NOW() | When scraped |
| linked_automatically | BOOLEAN | DEFAULT FALSE | Case matched by CNR |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** case_id, court_code, order_date, order_hash, tenant_id

---

### 7. forms
Legal form templates

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| court | VARCHAR(255) | NOT NULL | Court name |
| court_code | VARCHAR(50) | NOT NULL | e.g., "phhc", "sci" |
| form_type | VARCHAR(100) | NOT NULL | Type of form |
| form_name | VARCHAR(255) | NOT NULL | Display name |
| content | TEXT | NULL | Template content |
| fields | JSONB | DEFAULT '[]' | Form field definitions |
| instructions | TEXT | NULL | How to fill |
| is_active | BOOLEAN | DEFAULT TRUE | |

**Indexes:** court_code, form_type

---

### 8. ai_suggestions
AI compliance suggestions (from AIPOT-COMPLIANCE)

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| draft_id | UUID | FK → drafts.id, NOT NULL | Related draft |
| case_id | UUID | FK → cases.id, NULL | |
| check_type | VARCHAR(100) | NOT NULL | format, document, fee, cnr, party, timeline, language |
| suggestion | TEXT | NOT NULL | What to fix |
| severity | ENUM | NOT NULL | error, warning, info |
| line_reference | VARCHAR(255) | NULL | Where in document |
| fixed | BOOLEAN | DEFAULT FALSE | Whether addressed |
| fixed_at | TIMESTAMP | NULL | When fixed |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** draft_id, severity, tenant_id

---

### 9. tasks
To-do / task items

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| case_id | UUID | FK → cases.id, NULL | Related case |
| assigned_to | UUID | FK → advocates.id, NULL | Assignee |
| assigned_by | UUID | FK → advocates.id, NULL | Who assigned |
| title | VARCHAR(255) | NOT NULL | Task title |
| description | TEXT | NULL | Details |
| due_date | TIMESTAMP | NULL | Due date/time |
| priority | ENUM | DEFAULT 'normal' | low, normal, high, urgent |
| status | ENUM | DEFAULT 'pending' | pending, in_progress, completed, cancelled |
| completed_at | TIMESTAMP | NULL | When done |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** case_id, assigned_to, status, tenant_id

---

### 10. communications
WhatsApp/SMS/Email log (from AIPOT-COMMUNICATOR)

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| case_id | UUID | FK → cases.id, NULL | Related case |
| client_id | UUID | FK → clients.id, NULL | Recipient client |
| channel | ENUM | NOT NULL | whatsapp, sms, email, voice |
| direction | ENUM | NOT NULL | outbound, inbound |
| message_type | VARCHAR(50) | NOT NULL | reminder, alert, update, auto, manual |
| message | TEXT | NOT NULL | Message content |
| template_id | VARCHAR(100) | NULL | WhatsApp template ID |
| status | ENUM | DEFAULT 'sent' | queued, sent, delivered, read, failed |
| status_reason | VARCHAR(255) | NULL | Failure reason |
| recipient | VARCHAR(255) | NOT NULL | Phone or email |
| sent_at | TIMESTAMP | NULL | When sent |
| delivered_at | TIMESTAMP | NULL | When delivered |
| read_at | TIMESTAMP | NULL | When read |
| cost_inurred | DECIMAL(10,2) | NULL | SMS cost in INR |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** case_id, client_id, channel, status, created_at, tenant_id

---

### 11. invoices
Billing records

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| invoice_no | VARCHAR(50) | UNIQUE, NOT NULL | LETESE-INV-YYYY-NNNNN |
| advocate_id | UUID | FK → advocates.id, NOT NULL | Billed advocate |
| client_id | UUID | FK → clients.id, NULL | Billed client (optional) |
| case_id | UUID | FK → cases.id, NULL | Related case |
| amount | DECIMAL(10,2) | NOT NULL | Subtotal |
| gst_rate | DECIMAL(5,2) | DEFAULT 18.00 | GST percentage |
| gst_amount | DECIMAL(10,2) | NOT NULL | GST amount |
| total_amount | DECIMAL(10,2) | NOT NULL | Grand total |
| currency | VARCHAR(10) | DEFAULT 'INR' | |
| description | TEXT | NULL | Line items |
| status | ENUM | DEFAULT 'draft' | draft, sent, paid, overdue, cancelled, refunded |
| due_date | DATE | NULL | Payment due |
| paid_at | TIMESTAMP | NULL | When paid |
| razorpay_invoice_id | VARCHAR(255) | NULL | Razorpay invoice ID |
| razorpay_payment_id | VARCHAR(255) | NULL | Payment ID |
| pdf_url | VARCHAR(500) | NULL | Invoice PDF URL |
| sent_to_email | VARCHAR(255) | NULL | Email sent to |
| sent_at | TIMESTAMP | NULL | When sent |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** advocate_id, status, razorpay_invoice_id, tenant_id

---

### 12. payments
Payment transactions

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| invoice_id | UUID | FK → invoices.id, NULL | Related invoice |
| subscription_id | UUID | FK → subscriptions.id, NULL | If subscription payment |
| amount | DECIMAL(10,2) | NOT NULL | Amount paid |
| currency | VARCHAR(10) | DEFAULT 'INR' | |
| payment_method | VARCHAR(50) | NULL | upi, card, netbanking, wallet |
| status | ENUM | DEFAULT 'pending' | pending, success, failed, refunded |
| gateway | VARCHAR(50) | DEFAULT 'razorpay' | |
| razorpay_order_id | VARCHAR(255) | NULL | |
| razorpay_payment_id | VARCHAR(255) | NULL | |
| razorpay_signature | VARCHAR(255) | NULL | |
| gateway_response | JSONB | DEFAULT '{}' | Raw response |
| paid_at | TIMESTAMP | NULL | Successful payment time |
| refunded_at | TIMESTAMP | NULL | Refund time |
| refund_amount | DECIMAL(10,2) | NULL | |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** invoice_id, razorpay_order_id, status, tenant_id

---

### 13. landing_pages
Advocate branded pages (white-label)

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| advocate_id | UUID | FK → advocates.id, NOT NULL | |
| subdomain | VARCHAR(100) | UNIQUE, NOT NULL | e.g., "advocatename" |
| custom_domain | VARCHAR(255) | NULL | e.g., "law.advocatename.com" |
| title | VARCHAR(255) | NOT NULL | Page title |
| tagline | VARCHAR(255) | NULL | Subtitle |
| bio | TEXT | NULL | About the advocate |
| expertise | VARCHAR(255)[] | DEFAULT '{}' | Areas of practice |
| contact_phone | VARCHAR(20) | NULL | |
| contact_email | VARCHAR(255) | NULL | |
| is_published | BOOLEAN | DEFAULT FALSE | |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** advocate_id, subdomain, tenant_id

---

### 14. subscriptions
Plan subscriptions

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| advocate_id | UUID | FK → advocates.id, NOT NULL | |
| plan | ENUM | NOT NULL | basic, professional, elite, enterprise |
| billing_cycle | ENUM | DEFAULT 'monthly' | monthly, annual |
| amount | DECIMAL(10,2) | NOT NULL | Amount charged |
| status | ENUM | DEFAULT 'active' | active, cancelled, expired, trial |
| trial_ends_at | TIMESTAMP | NULL | |
| start_date | DATE | NOT NULL | Subscription start |
| end_date | DATE | NOT NULL | Current period end |
| cancelled_at | TIMESTAMP | NULL | When cancelled |
| cancel_reason | VARCHAR(255) | NULL | |
| auto_renew | BOOLEAN | DEFAULT TRUE | |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** advocate_id, status, end_date, tenant_id

---

### 15. audit_logs
All user actions (immutable)

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NULL | |
| user_id | UUID | NULL | Who did it |
| user_role | VARCHAR(50) | NULL | Their role at time |
| action | VARCHAR(100) | NOT NULL | e.g., "case_created", "payment_received" |
| entity_type | VARCHAR(50) | NULL | case, document, invoice, etc. |
| entity_id | UUID | NULL | ID of affected record |
| old_value | JSONB | NULL | Previous state |
| new_value | JSONB | NULL | New state |
| ip_address | VARCHAR(50) | NULL | |
| user_agent | VARCHAR(500) | NULL | |
| metadata | JSONB | DEFAULT '{}' | Extra context |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** user_id, entity_type+entity_id, action, created_at, tenant_id

---

### 16. deleted_data_archive
Soft-delete archive

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| original_table | VARCHAR(100) | NOT NULL | Where it came from |
| original_id | UUID | NOT NULL | ID in original table |
| data_json | JSONB | NOT NULL | Full record snapshot |
| deleted_by | UUID | FK → advocates.id, NOT NULL | Who deleted |
| reason | VARCHAR(255) | NULL | Why deleted |
| deleted_at | TIMESTAMP | NOT NULL | When deleted |

**Indexes:** original_table+original_id, tenant_id

---

## Missing Tables (TO CREATE)

### 17. tenants
Multi-tenant root table

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| name | VARCHAR(255) | NOT NULL | Firm/organization name |
| slug | VARCHAR(100) | UNIQUE, NOT NULL | URL-friendly name |
| plan | ENUM | DEFAULT 'basic' | basic, professional, elite, enterprise |
| storage_quota_bytes | BIGINT | DEFAULT 5368709120 | 5GB default |
| storage_used_bytes | BIGINT | DEFAULT 0 | |
| case_limit | INTEGER | DEFAULT 30 | |
| is_active | BOOLEAN | DEFAULT TRUE | |
| created_at | TIMESTAMP | DEFAULT NOW() | |

---

### 18. user_invites
Team invitation links

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| invite_email | VARCHAR(255) | NOT NULL | Email invite sent to |
| role | ENUM | NOT NULL | advocate, clerk, paralegal, intern |
| invited_by | UUID | FK → advocates.id, NOT NULL | Who invited |
| token | VARCHAR(255) | UNIQUE, NOT NULL | Invite token |
| status | ENUM | DEFAULT 'pending' | pending, accepted, expired, revoked |
| expires_at | TIMESTAMP | NOT NULL | Invite expiry |
| accepted_at | TIMESTAMP | NULL | When accepted |
| created_at | TIMESTAMP | DEFAULT NOW() | |

---

### 19. reminder_queue
Scheduled reminders

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| case_id | UUID | FK → cases.id, NOT NULL | Related case |
| client_id | UUID | FK → clients.id, NULL | Recipient client |
| channel | ENUM | NOT NULL | whatsapp, sms, email, voice |
| remind_at | TIMESTAMP | NOT NULL | When to send |
| message_template | VARCHAR(255) | NOT NULL | Template key |
| message_vars | JSONB | DEFAULT '{}' | {case_no, hearing_date, etc.} |
| status | ENUM | DEFAULT 'pending' | pending, sent, cancelled, failed |
| sent_at | TIMESTAMP | NULL | When actually sent |
| sent_by | VARCHAR(50) | NULL | "system" or "manual" |
| reminder_type | VARCHAR(50) | NOT NULL | 15_day, 7_day, 48_hour, 24_hour |
| created_at | TIMESTAMP | DEFAULT NOW() | |

---

### 20. case_checklists
Per-court filing checklists

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| court_code | VARCHAR(50) | NOT NULL | e.g., "phhc" |
| case_type | VARCHAR(100) | NOT NULL | CWP, CRM, etc. |
| checklist_items | JSONB | NOT NULL | [{item, required, order}] |
| version | INTEGER | DEFAULT 1 | Checklist version |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**Unique:** court_code + case_type

---

### 21. translation_jobs
Document translation jobs

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| document_id | UUID | FK → documents.id, NULL | Source document |
| from_lang | VARCHAR(10) | NOT NULL | e.g., "en", "hi", "pa" |
| to_lang | VARCHAR(10) | NOT NULL | |
| status | ENUM | DEFAULT 'queued' | queued, processing, completed, failed |
| accuracy_score | DECIMAL(5,2) | NULL | AI confidence score |
| result_document_id | UUID | FK → documents.id, NULL | Output document |
| error_message | TEXT | NULL | If failed |
| started_at | TIMESTAMP | NULL | |
| completed_at | TIMESTAMP | NULL | |
| created_at | TIMESTAMP | DEFAULT NOW() | |

---

### 22. voice_call_logs
AI voice call records

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| case_id | UUID | FK → cases.id, NULL | Related case |
| client_id | UUID | FK → clients.id, NULL | Called client |
| caller_number | VARCHAR(20) | NOT NULL | From number |
| callee_number | VARCHAR(20) | NOT NULL | To number |
| duration_seconds | INTEGER | NULL | Call duration |
| status | ENUM | DEFAULT 'initiated' | initiated, answered, missed, failed |
| recording_url | VARCHAR(500) | NULL | Recording URL |
| transcript | TEXT | NULL | Speech-to-text |
| summary | TEXT | NULL | AI summary |
| cost_inurred | DECIMAL(10,2) | NULL | Cost |
| called_at | TIMESTAMP | NOT NULL | |
| created_at | TIMESTAMP | DEFAULT NOW() | |

---

### 23. api_vendor_configs
Third-party API credentials (encrypted)

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| vendor_name | VARCHAR(50) | UNIQUE, NOT NULL | razorpay, 360dialog, msg91, sendgrid, elevenlabs |
| config_json | TEXT | NOT NULL | Encrypted JSON credentials |
| is_active | BOOLEAN | DEFAULT TRUE | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

---

### 24. scraper_jobs
Court scraping job queue

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NULL | NULL = system-wide job |
| case_id | UUID | FK → cases.id, NULL | Specific case scrape |
| court_code | VARCHAR(50) | NOT NULL | Which court |
| case_no | VARCHAR(100) | NULL | Specific case or NULL = all |
| status | ENUM | DEFAULT 'queued' | queued, running, completed, failed |
| priority | INTEGER | DEFAULT 5 | 1=highest, 10=lowest |
| attempts | INTEGER | DEFAULT 0 | Retry count |
| last_run | TIMESTAMP | NULL | |
| next_run | TIMESTAMP | NULL | |
| result | JSONB | DEFAULT '{}' | {new_orders: N, errors: []} |
| error_message | TEXT | NULL | Last error |
| created_at | TIMESTAMP | DEFAULT NOW() | |

---

### 25. vector_cache
Cached embeddings for RAG

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| case_id | UUID | FK → cases.id, NULL | Related case |
| content_hash | VARCHAR(64) | NOT NULL | SHA256 of content |
| content_type | VARCHAR(50) | NOT NULL | court_order, judgment, petition, etc. |
| content_text | TEXT | NOT NULL | The text |
| embedding | VECTOR | NOT NULL | pgvector column |
| model | VARCHAR(100) | NOT NULL | Embedding model used |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** case_id, content_hash, content_type

---

## Key Enums

```sql
CREATE TYPE user_role AS ENUM ('super_admin', 'advocate_admin', 'advocate', 'clerk', 'paralegal', 'intern', 'client');
CREATE TYPE plan_type AS ENUM ('basic', 'professional', 'elite', 'enterprise');
CREATE TYPE case_status AS ENUM ('active', 'disposed', 'dismissed', 'transferred', 'pending');
CREATE TYPE case_priority AS ENUM ('low', 'normal', 'high', 'urgent');
CREATE TYPE doc_type AS ENUM ('petition', 'order', 'judgment', 'evidence', 'correspondence', 'vakalatnama', 'affidavit', 'other');
CREATE TYPE draft_status AS ENUM ('draft', 'approved', 'filed', 'rejected');
CREATE TYPE invoice_status AS ENUM ('draft', 'sent', 'paid', 'overdue', 'cancelled', 'refunded');
CREATE TYPE payment_status AS ENUM ('pending', 'success', 'failed', 'refunded');
CREATE TYPE comm_channel AS ENUM ('whatsapp', 'sms', 'email', 'voice');
CREATE TYPE reminder_type AS ENUM ('15_day', '7_day', '48_hour', '24_hour');
CREATE TYPE subscription_status AS ENUM ('active', 'cancelled', 'expired', 'trial');
```

---

## Row-Level Security (RLS) Example

```sql
-- Set tenant context on each request
ALTER TABLE advocates ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON advocates
  FOR ALL USING (tenant_id = current_setting('app.tenant_id')::UUID);

-- Set before each query (in FastAPI middleware)
SET app.tenant_id = 'uuid-here';
```

---

## Migration Order

1. Create `tenants` table
2. Add `tenant_id` to existing tables (add column + backfill)
3. Create missing tables (17-25)
4. Create RLS policies
5. Update pricing in DB to match website
6. Test multi-tenant isolation
