# Letese — FlutterFlow Setup Plan

## Overview
FlutterFlow is a no-code/low-code platform for building cross-platform mobile apps. Letese app will be built using FlutterFlow with a custom FastAPI backend integration.

---

## Phase 1: Project Setup (Day 1)

### 1.1 Account & Workspace
- [ ] Create FlutterFlow account at [app.flutterflow.io](https://app.flutterflow.io)
- [ ] Create new project: **Letese**
- [ ] Set app name: "Letese" | Bundle ID: `com.letese.app`
- [ ] Choose theme: Light mode (dark mode later)
- [ ] Set primary color: **#2563EB** (blue) | Secondary: **#10B981** (green)

### 1.2 Global Settings
```
App Settings → General
├── App Name: Letese
├── Logo: Upload letese_logo.svg
├── Primary Color: #2563EB
├── Secondary Color: #10B981
├── Accent Color: #F59E0B
├── Error Color: #EF4444
├── Background: #F8FAFC
├── Font Family: Inter (Google Fonts)
└── App Version: 1.0.0

App Settings → Security
├── Enable HTTPS: ON
├── Disable Right Click: ON
├── Disable Text Selection: OFF (accessibility)
└── Biometric Auth: Optional (for high-security actions)

App Settings → Navigation
├── Bottom Nav Bar: ON (4 tabs)
├── Splash Screen: Custom with logo
├── Onboarding: 3 screens (first-time users)
└── Deep Linking: Enabled
```

---

## Phase 2: Authentication Screens (Day 1-2)

### Screen 1: Splash Screen
```
Components:
├── Background: Gradient (#2563EB → #1D4ED8)
├── Center: Logo (150x150, animated fade-in)
├── Bottom: Tagline "Legal Services, Simplified"
└── Auto-navigate: After 2.5s → Check Auth → Login/Onboarding/Home
```

### Screen 2: Onboarding (First-time users only)
```
3 Pages with PageView:

Page 1 — "Register Your Business"
├── Image: Business registration illustration
├── Title: "Company Registration Made Easy"
└── Subtitle: "Private Ltd, LLP, OPC — we handle everything"

Page 2 — "Fire NOC Compliance"
├── Image: Fire safety illustration
├── Title: "Fire NOC Without the Hassle"
└── Subtitle: "Expert guidance through the entire process"

Page 3 — "Track Everything"
├── Image: Case tracking illustration
├── Title: "Real-time Case Tracking"
└── Subtitle: "Know exactly where your application stands"

Navigation:
├── Skip button (top-right)
├── Page indicators (dots)
├── Next button → Page 2 → Page 3 → Login
└── "Get Started" on last page → Login
```

### Screen 3: Login Screen
```
Fields:
├── Email: Text Field (keyboard: email)
├── Password: Text Field (obscured, toggle visibility icon)
└── Remember Me: Checkbox

Buttons:
├── "Sign In" → Primary button → Validate → Call /auth/login API
└── "Forgot Password?" → Text button → Forgot Password flow

Social Login (future):
├── Google Sign In button
└── "Don't have an account? Sign Up" → Register

Validation:
├── Email: Required, valid format
├── Password: Required, min 8 chars
└── Show inline errors below field
```

### Screen 4: Register Screen
```
Fields:
├── Full Name: Text Field
├── Email: Text Field (keyboard: email)
├── Phone: Text Field (phone keyboard, +91 prefix)
└── Password: Text Field (obscured, strength indicator)
├── Confirm Password: Text Field
└── Terms: Checkbox "I agree to Terms & Privacy Policy"

Buttons:
├── "Create Account" → Primary → Call /auth/register API
└── "Already have an account? Sign In"

Validation:
├── All fields required
├── Email: Valid format, check uniqueness via API
├── Phone: 10 digits, Indian format
├── Password: min 8 chars, 1 uppercase, 1 number
└── Confirm: Must match password
```

### Screen 5: OTP Verification Screen
```
Fields:
├── 6-digit OTP input (individual boxes, auto-focus next)
├── Resend OTP timer (60s countdown)
└── "Didn't receive code?" + Resend link

Flow:
├── OTP sent to email/phone on register
├── Auto-submit when 6 digits entered
├── Validate via /auth/verify-otp API
├── On success → Set user as verified → Go to Home
└── Wrong OTP: Shake animation + error message
├── Max 3 attempts, then lock 5 minutes
```

### Screen 6: Forgot Password Screen
```
Flow:
├── Enter email → Send OTP
├── Verify OTP
├── Enter new password + confirm
└── Reset → Login screen

States:
├── Email sent (show checkmark + "Check your email")
├── OTP verified
└── Password reset success → Login
```

---

## Phase 3: Home / Dashboard (Day 2-3)

### Screen 7: Bottom Navigation Bar
```
4 Tabs:
├── 🏠 Home (Dashboard)
├── 📁 My Cases
├── 💬 Messages
└── 👤 Profile

Design:
├── Active: Primary color icon + label
├── Inactive: Grey icon, no label
├── Badge on Messages tab if unread count > 0
└── Smooth transition animation
```

### Screen 8: Home / Dashboard Screen
```
Header:
├── Greeting: "Hi, [Full Name]" (with time-based: Good morning/afternoon/evening)
├── Notification bell icon (top-right) → Notifications list
└── Profile avatar (top-right) → Quick profile menu

Hero Card (if active cases):
├── "Active Cases: X"
├── Current status badge
├── "Track" button → Case detail
└── Swipe up for summary

Quick Actions Grid (2x2):
├── 📋 Company Registration
├── 🔥 Fire NOC
├── 🧾 CA Services
└── ⚖️ Legal Advisory
├── [+ New Request] → Full service catalog

Stats Row:
├── "Completed Cases: X"
├── "In Progress: Y"
└── "Total Spent: ₹Z"

Recent Activity (ListView):
├── Last 3 case updates
├── Each: Service icon, case number, status, time ago
└── "View All" → My Cases
```

### Screen 9: Service Catalog / Browse Services
```
Layout:
├── Search bar (top)
├── Category chips (horizontal scroll): All, Company Reg, Fire NOC, CA, CS, Legal
└── Service cards grid (2 columns)

Service Card:
├── Icon (40x40, category color)
├── Service name
├── Starting price ("From ₹X")
├── Estimated time ("X-Y days")
├── Rating (stars, if reviews enabled)
└── "Learn More" button

Categories:
├── Company Registration
│   ├── Private Limited Company
│   ├── Public Limited Company
│   ├── One Person Company (OPC)
│   ├── LLP Registration
│   └── Foreign Company Branch
├── Fire NOC
│   ├── Fire NOC for Buildings
│   ├── Fire NOC for Factories
│   └── Fire NOC Renewal
├── CA Services
│   ├── GST Registration & Filing
│   ├── Income Tax Return
│   ├── ROC Compliance
│   └── Tax Planning
├── CS Services
│   ├── DIN/KYC
│   ├── Annual Filing
│   └── Director Compliance
└── Legal Advisory
    ├── Legal Notice Drafting
    ├── Contract Review
    └── Court Appearance (Remote)
```

### Screen 10: Service Detail Screen
```
Layout:
├── Hero: Service icon + gradient background
├── Service name (H2)
├── Category badge
├── Rating + completed count
├── Starting price + estimated time

About Section:
├── Description
├── "What's Included" list (bullets)
├── Required documents (collapsible)
└── Process timeline (numbered steps)

Pricing Card (sticky bottom):
├── Base price
├── "Book Now" → Case creation flow
└── "Talk to Expert" → Chat

Variants (if multiple subtypes):
├── Radio button list of subtypes
├── Each: name, price, description
└── Selected variant drives form fields
```

---

## Phase 4: Case Creation Flow (Day 3-4)

### Screen 11: Case Creation — Step 1 (Service Selection)
```
Layout:
├── Step indicator: "Step 1 of 4"
├── Title: "What do you need help with?"
├── Search services (if coming from Quick Action)
└── Selected service card (if pre-selected)
    ├── Service name, icon, price
    └── "Change" link
```

### Screen 12: Case Creation — Step 2 (Form Details)
```
Dynamic form based on service:
├── Fields defined in service_subtypes.form_fields (from DB)
├── Fields vary per service type

Common Fields:
├── State: Dropdown (all Indian states)
├── City: Text
├── Pincode: Text (6 digits)
├── Business Name: Text (for company registration)
├── Type of Entity: Dropdown (based on service)
├── Capital: Number (INR)
└── Number of Directors/Partners: Number

Validation:
├── Required fields marked with *
├── Real-time validation
└── Error messages below fields

Navigation:
├── "Back" → Step 1
└── "Next" → Step 3 (documents)
```

### Screen 13: Case Creation — Step 3 (Documents)
```
Layout:
├── Step indicator: "Step 3 of 4"
├── Document checklist (from service_subtypes.documents_required)
├── Each document item:
│   ├── Icon (uploaded ✓ / pending ⏳)
│   ├── Document name
│   ├── Format accepted: PDF, JPG, PNG (max 10MB)
│   └── Upload button → Camera / Gallery picker

Upload States:
├── Empty: Upload button (dashed border)
├── Uploading: Progress bar
├── Uploaded: File name + Remove button + Green checkmark
├── Rejected: Red X + reason text + Re-upload button

Camera/Gallery:
├── "Take Photo" → Camera
├── "Choose from Gallery"
└── Compress to max 2MB before upload

Navigation:
├── "Back" → Step 2
└── "Next" → Step 4 (Review) — only enabled if all required docs uploaded
```

### Screen 14: Case Creation — Step 4 (Review & Submit)
```
Layout:
├── Step indicator: "Step 4 of 4"
├── Title: "Review Your Request"

Sections (collapsible):
├── Service Details
│   ├── Service: [Name]
│   ├── Subtype: [Selected variant]
│   └── State/City: [Location]
├── Form Data
│   └── All entered form fields (read-only)
├── Documents
│   └── List of uploaded files with status
└── Pricing
    ├── Base Price: ₹X
    ├── Government Fees: ₹Y (estimated)
    └── Total: ₹Z

Disclaimer:
├── "Fees are estimates. Final amount may vary based on your case."
└── Terms checkbox: "I agree to the Terms of Service"

Buttons:
├── "Back" → Step 3
└── "Submit Request" → Call /cases API → Show success → Go to Case Detail
```

### Screen 15: Case Submission Success
```
Layout:
├── Animated checkmark (green)
├── "Request Submitted! 🎉"
├── Case Number: LET-2026-XXXXX
├── "We'll review your application within 24 hours"
├── "Assigned Expert: [Name]" (if auto-assigned)
└── "Track Status" button → Case Detail
├── "Go to Dashboard" button
```

---

## Phase 5: My Cases (Day 4-5)

### Screen 16: My Cases List
```
Layout:
├── Tab bar: All | Active | Completed | Cancelled
├── Search bar (search by case number, business name)
├── Sort: Newest First | Oldest First | Status
└── Case cards (ListView)

Case Card:
├── Case Number: LET-2026-XXXXX (tap to copy)
├── Service name + subtype
├── Status badge (colored by status)
├── State/City
├── Submitted date
├── Assigned expert: Avatar + Name (if assigned)
├── Progress indicator: horizontal stepper (submitted → review → docs → progress → complete)
├── Unread message indicator (dot)
└── Tap → Case Detail

Empty State:
├── "No cases yet"
├── "Ready to get started?"
└── "Browse Services" button
```

### Screen 17: Case Detail Screen
```
Header:
├── Case Number (tap to copy)
├── Status badge (large, colored)
├── Service name + subtype
├── Assigned expert card (if assigned)
│   ├── Avatar, Name, Role (CA/CS/Lawyer)
│   ├── "Call" button (if phone available)
│   └── "Message" button

Progress Timeline (vertical stepper):
├── Submitted ✓ (date)
├── Under Review ✓ (date)
├── Documents Pending ⏳ (current)
├── In Progress ⏳
├── Pending Payment ⏳
└── Completed ⏳

Case Details Section:
├── All form data (read-only, collapsible groups)
├── State: [Value]
├── City: [Value]
└── Business Name: [Value]

Documents Section:
├── "Documents" header + count
├── Uploaded documents list
│   ├── Each: Name, status badge (uploaded/verified/rejected)
│   ├── Tap to view (PDF/image viewer)
│   └── If rejected: Show reason + re-upload button
└── "Upload More Documents" button

Messages Section:
├── "Messages" header + unread count
├── Last message preview
├── "View All Messages" → Chat thread
└── "Ask a Question" → Quick message input

Actions:
├── "Download Receipt" (if completed)
├── "Raise Support Ticket" (if issues)
└── "Cancel Case" (if not in final stages) — confirmation dialog
```

### Screen 18: Case Chat / Messages Thread
```
Layout:
├── Header: Case number + service name
├── Expert info strip (name, role, online status)
├── Message bubbles:
│   ├── User messages: Right-aligned, blue background
│   ├── Expert messages: Left-aligned, grey background
│   ├── System messages: Center, small, grey text (status changes)
│   ├── Document attachments: Thumbnail + filename + download
│   └── Timestamps: Grouped by day
├── Unread: Unread divider line

Input Area (sticky bottom):
├── Text input (multiline, auto-expand up to 4 lines)
├── Attach button (document/camera)
├── Send button (arrow icon)
└── "Expert usually replies within 2 hours" hint

States:
├── Loading: Skeleton messages
├── Empty: "No messages yet. Start the conversation!"
├── Sending: Show message with clock icon
└── Error: Red icon + "Tap to retry"
```

---

## Phase 6: Profile & Settings (Day 5)

### Screen 19: Profile Screen
```
Layout:
├── Profile header:
│   ├── Avatar (tap to change, circular, 100px)
│   ├── Full Name
│   ├── Email (verified badge ✓ / ✗)
│   ├── Phone (verified badge ✓ / ✗)
│   └── "Edit Profile" button

Account Section:
├── Personal Information → Edit name, phone, email
├── Change Password
├── Business Information (if applicable)
└── KYC / ID Verification

Preferences:
├── Language: English / हिंदी
├── Notifications Settings
│   ├── Case Updates: Toggle
│   ├── Payment Alerts: Toggle
│   ├── New Messages: Toggle
│   └── Promotional: Toggle
└── Biometric Login: Toggle

Support:
├── Help Center → WebView / FAQ
├── Raise a Ticket → Support form
├── Chat with Us → In-app chat
└── Call Support: +91-XXXXXXXXXX

Legal:
├── Terms of Service
├── Privacy Policy
└── Refund Policy

Account:
├── Deactivate Account
├── Delete Account (with confirmation)
└── Sign Out

App Info:
├── Version: 1.0.0
└── "Check for Updates"
```

---

## Phase 7: Notifications & Misc (Day 5-6)

### Screen 20: Notifications List
```
Layout:
├── "Notifications" header
├── "Mark All as Read" (top right)
├── Filter: All | Unread
└── Notification cards (ListView)

Notification Card:
├── Icon (based on type: case/payment/message/system)
├── Title (bold)
├── Message body (truncated to 2 lines)
├── Time ago (e.g., "2 hours ago")
├── Unread dot (blue, left side)
└── Tap → Navigate to relevant screen (case detail, payment, etc.)

Types:
├── 🔄 Case Status Update — "Your case LET-2026-001 is now under review"
├── 💳 Payment Received — "Payment of ₹X received for LET-2026-001"
├── 📄 Document Verified — "Aadhar Card has been verified"
├── ⏰ Reminder — "Submit pending documents for LET-2026-001"
└── 📢 System — "New service available: OPC Registration"
```

### Screen 21: Support / Raise Ticket
```
Form:
├── Subject: Text input
├── Category: Dropdown (Technical, Billing, Service Issue, Other)
├── Case Reference: Optional (link to existing case)
├── Description: Text area (multiline)
├── Attachments: Up to 3 files
└── Priority: Normal / Urgent

Submit → Success confirmation + ticket number
```

---

## Phase 8: Payment Flow (Future / v0.2)

### Payment Screen
```
Layout:
├── Order summary card
├── Amount breakdown:
│   ├── Service Fee: ₹X
│   ├── Government Fee: ₹Y
│   └── Total: ₹Z
├── Payment method selection:
│   ├── UPI (default, recommended)
│   ├── Credit/Debit Card
│   ├── Net Banking
│   └── Wallet
├── "Pay ₹Z" button → Payment gateway
├── Secure payment badge
└── "100% Secure | Powered by Razorpay"
```

---

## FlutterFlow API Integration

### Backend API Endpoints to Connect

```
Base URL: https://api.letese.xyz/v1

Authentication:
POST /auth/register        → Create account
POST /auth/login           → Login (returns JWT)
POST /auth/verify-otp      → Verify OTP
POST /auth/forgot-password → Request password reset
POST /auth/refresh-token   → Refresh JWT

User:
GET  /users/me             → Get current user profile
PUT  /users/me             → Update profile
POST /users/me/avatar      → Upload avatar

Services:
GET /services              → List all services
GET /services/{slug}       → Service detail + subtypes

Cases:
GET  /cases                → List user's cases
POST /cases                → Create new case
GET  /cases/{id}           → Case detail
PUT  /cases/{id}           → Update case
POST /cases/{id}/cancel    → Cancel case

Documents:
POST /cases/{id}/documents → Upload document
GET  /cases/{id}/documents → List documents
DELETE /documents/{id}     → Delete document

Messages:
GET  /cases/{id}/messages        → Get messages
POST /cases/{id}/messages        → Send message

Payments:
POST /payments/initiate    → Create order
POST /payments/webhook     → Payment confirmation (Razorpay)
GET  /payments/{id}        → Payment status

Notifications:
GET  /notifications        → User notifications
PUT  /notifications/{id}/read → Mark as read
PUT  /notifications/read-all   → Mark all read
```

### FlutterFlow Variables (Global)

```
AuthToken (stored in Local Storage)
CurrentUser (custom state)
SelectedService (custom state)
ActiveCaseId (custom state)
NotificationCount (custom state)
IsDarkMode (custom state)
Language (custom state: en/hi)
```

---

## Component Library (Reusable)

### Custom Components to Build:
- [ ] `PrimaryButton` — Blue filled button, loading state
- [ ] `SecondaryButton` — Outlined button
- [ ] `TextInputField` — With label, error, helper text
- [ ] `PasswordField` — With visibility toggle
- [ ] `OTPInput` — 6-box OTP entry
- [ ] `StatusBadge` — Colored badge by status
- [ ] `CaseCard` — Reusable case list item
- [ ] `ServiceCard` — Service grid item
- [ ] `DocumentUploadItem` — With upload progress
- [ ] `StepIndicator` — Horizontal stepper
- [ ] `TimelineItem` — Vertical timeline step
- [ ] `AvatarWithStatus` — User avatar + online dot
- [ ] `EmptyState` — Icon + message + CTA
- [ ] `LoadingOverlay` — Full screen loader
- [ ] `ConfirmationDialog` — Modal with confirm/cancel
- [ ] `BottomSheetMenu` — For action menus
- [ ] `ShimmerLoader` — Skeleton loading states
```

---

## Deployment Checklist

- [ ] Enable Push Notifications (Firebase Cloud Messaging)
- [ ] Configure Deep Links (letese://)
- [ ] App Store Connect: Create iOS app listing
- [ ] Google Play Console: Create Android listing
- [ ] App Icons: Generate all sizes (1024x1024 master)
- [ ] Splash Screen assets
- [ ] Onboarding illustrations (3 images)
- [ ] Empty state illustrations
- [ ] Error page illustrations
- [ ] Privacy Policy URL
- [ ] Terms of Service URL
- [ ] Support email: support@letese.co
- [ ] Test on iOS simulator
- [ ] Test on Android emulator
- [ ] Test on real devices (iOS + Android)
- [ ] Run FlutterFlow analyzers (no errors)
- [ ] Build for iOS (TestFlight)
- [ ] Build for Android (Internal testing track)
- [ ] Submit for review (App Store + Play Store)
