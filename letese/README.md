# Letese — Legal Tech Platform

> Legal services SaaS platform for Indian businesses — company registration, compliance, Fire NOC, CA/CS services, and legal advisory.

---

## 📁 Project Structure

```
letese/
├── docs/                          # Complete project documentation
│   ├── 01-project-overview.md     # What is Letese, mission, tech stack
│   ├── 02-database-schema.md      # PostgreSQL schema — 12 tables, all columns
│   ├── 03-flutterflow-setup.md    # FlutterFlow screens — step-by-step setup
│   ├── 04-fastapi-backend-structure.md  # FastAPI file-by-file structure
│   └── 05-user-flows.md           # All user flows — registration to payment
│
└── README.md                      # This file
```

---

## 📋 Documentation Index

| Doc | What it covers |
|-----|---------------|
| `01-project-overview.md` | What Letese is, mission, services, tech stack, target users |
| `02-database-schema.md` | 12 PostgreSQL tables, every column, type, index, enum, relationship |
| `03-flutterflow-setup.md` | 20+ FlutterFlow screens, every component, field, API integration, deployment |
| `04-fastapi-backend-structure.md` | Every backend file, function, API route, service layer, migration |
| `05-user-flows.md` | 10 complete user flows: login, registration, case creation, payment, chat, admin |

---

## 🚀 Development Phases

### Phase 1: Foundation
- [ ] Setup PostgreSQL database
- [ ] Run initial Alembic migration
- [ ] Seed services data (`scripts/seed_services.py`)
- [ ] Create first admin user (`scripts/create_admin.py`)

### Phase 2: Backend API
- [ ] Auth: Register, Login, OTP, JWT, Refresh tokens
- [ ] Users: Profile, Avatar upload
- [ ] Services: CRUD, listing, categories
- [ ] Cases: Create, Submit, Update, List, Detail, Status history
- [ ] Documents: Upload (S3), Download (presigned URL), Verify
- [ ] Messages: Case chat thread
- [ ] Payments: Razorpay integration
- [ ] Notifications: In-app + Email

### Phase 3: FlutterFlow Frontend
- [ ] Auth screens (Login, Register, OTP, Forgot Password)
- [ ] Home / Dashboard
- [ ] Service Catalog + Detail
- [ ] Case Creation (4-step wizard)
- [ ] My Cases list + Detail
- [ ] Case Chat
- [ ] Profile & Settings
- [ ] Notifications
- [ ] Payment flow

### Phase 4: Admin Panel
- [ ] Admin dashboard
- [ ] Case management (all cases, filters, bulk actions)
- [ ] Document verification UI
- [ ] User management
- [ ] Analytics & reporting

---

## ⏱️ Time Estimates

| Task | Estimated Time |
|------|---------------|
| Documentation (this phase) | ✅ Complete |
| Backend API (full) | 7–10 days |
| FlutterFlow frontend | 14–18 days |
| Admin panel | 5–7 days |
| Testing + bug fixes | 5–7 days |
| Deployment + monitoring | 2–3 days |
| **Total** | **~1.5 – 2 months** |

---

## 🔗 Key Links

- **FlutterFlow**: https://app.flutterflow.io
- **Backend API**: https://api.letese.xyz
- **Admin Panel**: https://admin.letese.xyz
- **Website**: https://letese.xyz
- **Support**: support@letese.co

---

## 📅 Created

- **Date**: 2026-04-27
- **Phase**: Planning & Documentation
- **Status**: 🟡 In Progress

_Last updated: 2026-04-27_
