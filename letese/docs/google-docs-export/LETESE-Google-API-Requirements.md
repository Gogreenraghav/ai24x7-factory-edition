LETESE — Google API Requirements Checklist
For: Google Cloud Team
## Date: 27 April 2026
1. Gemini API Access
Needed Now:
| Item | Details | Status |
|------|---------|--------|
| API Key / Service Account | JSON credentials file | NEED |
| Project ID | gmail-oauth-492922 (existing) | OK |
| Region | asia-south-1 (Mumbai) | PREFERRED |
| Free Trial Credits | ₹10,000 minimum | NEED |
Models Required:
| Model | Purpose | Context Window |
|-------|---------|---------------|
| gemini-2.0-pro | Complex petitions | 1M tokens |
| gemini-1.5-flash | Fast queries, summaries | 128K tokens |
| gemini-1.5-pro-vision | Court order OCR | Images + text |
| gemini-embedding-001 | Vector embeddings | Text only |
###配额:
- Monthly budget: ₹50,000-2,00,000 (scales with usage)
- Expected API calls: 10,000-1,00,000/month (scales with users)
2. Service Account Setup
**Need from Google:**
1. Service account JSON key file
2. IAM roles: Vertex AI User, Gemini API User, Drive API Editor
3. Domain-wide delegation for Gmail API (arjun.raghav93@gmail.com)
**Permissions needed:**
- gmail.send (send emails)
- drive.file (create files in Drive)
- sheets (create/update spreadsheets)
- docs (create documents)
- calendar (create meet events)
3. Vertex AI Vector Search
**Need:**
- Enable Vertex AI API on project
- Enable Vector Search API
- Create first vector index
- Embedding model: text-embedding-005
- Index destination: asia-south-1
**Dimensions:** 768 (text-embedding-005)
**Algorithm:** HNSW (for <1M vectors), AUtoMERGE (for >1M)
4. Google for Startups Credits
**Apply for:** Google for Startups Cloud Program India
**Expected ask:** ₹10,00,000 (₹10 lakh / ₹1 million)
**Use:**
- Gemini API calls: ₹3,00,000
- Vertex AI Vector Search: ₹2,00,000
- Cloud Run (scaling): ₹2,00,000
- Cloud Storage + CDN: ₹1,00,000
- Support + Monitoring: ₹2,00,000
5. Google Workspace (if applicable)
**Ask from Arjun's existing account:**
- Already using: Google Drive, Gmail, Google Meet
- Additional needed: Google Docs API, Sheets API
6. Technical Questions
| Question | Why We Need to Know |
|----------|-------------------|
| Data residency for court data | Legal data must stay in India |
| Rate limits for Gemini API | Need for our load balancer design |
| Caching allowed? | We want to cache embeddings (1 hour TTL) |
| On-premise deployment option? | Some clients may want data on their servers |
| SLA for Gemini API | Need 99.5% uptime guarantee |
7. Integration Checklist
| Integration | API | Priority | Status |
|-------------|-----|----------|--------|
| Gemini Ultra for drafting | Vertex AI | 🔴 HIGH | NEED ACCESS || Gemini Vision for OCR | Vertex AI Vision | 🔴 HIGH | NEED ACCESS || Legal research search | Vertex Vector Search | 🔴 HIGH | NEED ENABLE || Agentic court monitoring | Gemini Agentic | 🟡 MEDIUM | NEED INFO || Auto document backup | Drive API | 🟡 MEDIUM | READY || Email notifications | Gmail API | 🟢 LOW | READY || Analytics export | Sheets API | 🟢 LOW | READY || Client video calls | Meet API | 🟢 LOW | FUTURE |
8. Action Items — What We Need from Google
This Week:
- [ ] Gemini API free trial activated (₹10,000 credits)
- [ ] Service account JSON key file shared
- [ ] Vertex AI Vector Search enabled
- [ ] Confirmation of asia-south-1 region availability
This Month:
- [ ] Google for Startups application submitted
- [ ] ₹10 lakh credits approved (or maximum available)
- [ ] Technical architecture review scheduled
- [ ] Security/compliance review completed
Long-term:
- [ ] Dedicated TAM assigned
- [ ] Quarterly business reviews
- [ ] Co-marketing agreement
