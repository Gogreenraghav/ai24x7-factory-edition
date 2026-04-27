# Letese — User Flow Diagrams

## Legend
```
[Action]          = User takes an action
(Decision)        = Branch point
{Screen}          = FlutterFlow screen
<API Call>        = Backend API call
[Notification]    = System sends notification
→                 = Flow direction
```

---

## Flow 1: User Registration & Login

```
┌─────────────────────────────────────────────────────────────┐
│                    REGISTRATION FLOW                         │
└─────────────────────────────────────────────────────────────┘

[User taps "Sign Up" on Login Screen]
          │
          ▼
    {Register Screen}
          │
          ▼
  [Enter: Full Name, Email, Phone, Password]
          │
          ▼
  <POST /auth/register>  ──(email/phone + OTP sent)──→  Backend
          │
          │  ✅ 200: "OTP sent to email"
          ▼
    {OTP Verification Screen}
          │
          ▼
  [Enter 6-digit OTP]  ──(auto-submit on 6 digits)──→  <POST /auth/verify-otp>
          │
          │  ✅ Verified
          ▼
    <POST /auth/login>  ──(returns JWT tokens)──→  Backend
          │
          │  ✅ Token stored in localStorage
          ▼
    {Onboarding (first time only)}  ──or──→  {Home Screen}
          │
          ▼
    [Swipe through 3 pages] → [Tap "Get Started"]
          │
          ▼
    {Home Screen}  ✅ Registration Complete


┌─────────────────────────────────────────────────────────────┐
│                      LOGIN FLOW                              │
└─────────────────────────────────────────────────────────────┘

[User opens app]  ──(has valid token?)──→  NO → {Login Screen}
         │
         │ YES
         ▼
    {Home Screen}  ✅ Already logged in


[User taps "Sign In" on Login Screen]
          │
          ▼
    {Login Screen}
          │
          ▼
  [Enter: Email, Password]
          │
          ▼
  <POST /auth/login>  ──(returns JWT tokens)──→  Backend
          │
          │  ✅ 200: {access_token, refresh_token}
          │  ❌ 401: "Invalid credentials"
          │  ❌ 403: "Please verify your email first"
          ▼
    [Success?]
     YES ──→  {Home Screen}
     NO ──→  [Show error below form] → [User corrects and retries]


┌─────────────────────────────────────────────────────────────┐
│                   FORGOT PASSWORD FLOW                       │
└─────────────────────────────────────────────────────────────┘

[User taps "Forgot Password?"]
          │
          ▼
    {Forgot Password Screen}
          │
          ▼
  [Enter registered email]
          │
          ▼
  <POST /auth/forgot-password>  ──(OTP sent)──→  Backend
          │
          │  ✅ 200: "Reset code sent"
          ▼
    {OTP Verification (Reset)}  ──or──→  {Email received}
          │
          ▼
  [Enter OTP + New Password + Confirm Password]
          │
          ▼
  <POST /auth/reset-password>  ──(validates OTP + resets)──→  Backend
          │
          │  ✅ 200: "Password reset successful"
          ▼
    {Login Screen}
```

---

## Flow 2: Browse Services & Select

```
[User taps any Quick Action on Home]
         │
         │         [User taps "Browse Services" on Home]
         │                      │
         ▼                      ▼
   {Service Detail}    {Service Catalog Screen}
         │                      │
         │                      ▼
         │           [Search bar / Category filter]
         │                      │
         │                      ▼
         │           [Service cards grid displayed]
         │                      │
         ▼                      ▼
   [Tap "Book Now"]      [Tap Service Card]
         │                      │
         │                      ▼
         │            {Service Detail Screen}
         │                      │
         ▼                      ▼
   [Proceed to Case Creation Step 1]


{SERVICE DETAIL SCREEN}

    ┌──────────────────────────────────────────┐
    │  🔥 Fire NOC for Buildings               │
    │  Category: Fire NOC                      │
    │  ⭐ 4.8 (124 reviews)                    │
    │  From ₹15,000 | Est. 15-30 days          │
    ├──────────────────────────────────────────┤
    │  About                                   │
    │  Complete Fire NOC assistance from       │
    │  application to approval...              │
    ├──────────────────────────────────────────┤
    │  What's Included                         │
    │  ✅ Application drafting                  │
    │  ✅ Document verification                 │
    │  ✅ Submission assistance                 │
    │  ✅ Status tracking                       │
    │  ✅ NOC delivery                          │
    ├──────────────────────────────────────────┤
    │  Required Documents                       │
    │  📄 Building Plan Approval               │
    │  📄 Property Documents                   │
    │  📄 Identity Proof                       │
    │  📄 Address Proof                       │
    │  ▶ Show all 8 documents                  │
    ├──────────────────────────────────────────┤
    │  Process Timeline                        │
    │  ① Document Collection (Day 1-2)          │
    │  ② Application Drafting (Day 3-4)          │
    │  ③ Submission to Fire Dept (Day 5)       │
    │  ④ Inspection Support (Day 15-20)        │
    │  ⑤ NOC Received (Day 20-30)              │
    └──────────────────────────────────────────┘

    ┌──────────────────────────────────────────┐
    │  From ₹15,000  │  [Book Now]  │ 💬 Talk]  │
    └──────────────────────────────────────────┘
```

---

## Flow 3: Case Creation (Full Step-by-Step)

```
┌─────────────────────────────────────────────────────────────┐
│                  CASE CREATION FLOW                         │
│           (4-Step Wizard — 1 Hour to Complete)             │
└─────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════
 STEP 1: SELECT SERVICE VARIANT (if applicable)
═══════════════════════════════════════════════════════════════

{Step 1 of 4 — Select Service}
          │
          ▼
    [If service has subtypes]
    ┌──────────────────────────────────┐
    │  Select Type:                    │
    │  ○ Private Limited Company  ₹59,999│
    │  ● One Person Company      ₹29,999│
    │  ○ LLP Registration        ₹39,999│
    └──────────────────────────────────┘
          │
          │  [Service has no subtypes → skip to Step 2]
          ▼
    [Tap "Next"]
          │
          ▼
═══════════════════════════════════════════════════════════════
 STEP 2: FILL DETAILS (Dynamic Form)
═══════════════════════════════════════════════════════════════

{Step 2 of 4 — Your Details}
     (Form fields driven by service_subtypes.form_fields from DB)

    Example for Company Registration:
    ┌──────────────────────────────────┐
    │  Business Details                │
    │                                  │
    │  Business/Company Name *         │
    │  [________________________]      │
    │                                  │
    │  State *                         │
    │  [Delhi ________________▼]       │
    │                                  │
    │  City *                          │
    │  [________________________]      │
    │                                  │
    │  Pincode *                       │
    │  [__________]                    │
    │                                  │
    │  No. of Directors *              │
    │  [  2  ] [+] [-]                │
    │                                  │
    │  Director 1 Details              │
    │  Name: [__________________]     │
    │  DIN:  [__________________]     │
    │  PAN:  [__________________]     │
    │  Aadhar: [________________]     │
    │  Email: [__________________]    │
    │                                  │
    │  Director 2 Details              │
    │  ... same fields ...             │
    │                                  │
    │  Authorized Capital *            │
    │  [₹ 1,00,000 ▼        ]          │
    │  (1L | 5L | 10L | 25L | Custom) │
    │                                  │
    │  Registered Office Address *    │
    │  [__________________________]   │
    │  [__________________________]   │
    │                                  │
    └──────────────────────────────────┘

          │
          │  Validation: All * fields required
          │  Real-time: Red border + error text on blur
          ▼
    [Tap "Next"]
          │
          ▼
═══════════════════════════════════════════════════════════════
 STEP 3: UPLOAD DOCUMENTS
═══════════════════════════════════════════════════════════════

{Step 3 of 4 — Documents}
     (Checklist from service_subtypes.documents_required)

    ┌──────────────────────────────────────────┐
    │  📋 Required Documents                    │
    │                                           │
    │  ⏳ Aadhar Card (All Directors)           │
    │     Tap to upload                         │
    │                                           │
    │  ⏳ PAN Card (All Directors)              │
    │     Tap to upload                         │
    │                                           │
    │  ⏳ Passport Photo (All Directors)        │
    │     Tap to upload                         │
    │                                           │
    │  ⏳ Address Proof                        │
    │     [Uploaded ✓]  filename.jpg           │
    │     [Remove]  [View]                      │
    │                                           │
    │  ⏳ Business Address Proof               │
    │     [Uploaded ✓]  rent_agreement.pdf     │
    │                                           │
    │  ⏳ No Objection Certificate             │
    │     Notarized NOC from property owner    │
    │     [Upload]                              │
    │                                           │
    │  ─────────────────────────────────────── │
    │  📎 Optional Documents                    │
    │  ⏳ DIN (if already available)            │
    │  ⏳ Existing Trademark (if any)           │
    │                                           │
    └──────────────────────────────────────────┘

    [Tap on document] → Bottom Sheet:
    ┌──────────────────────────────────┐
    │  Upload Aadhar Card              │
    │                                  │
    │  📷 Take Photo                  │
    │  🖼️ Choose from Gallery         │
    │                                  │
    │  Accepted: PDF, JPG, PNG         │
    │  Max size: 10MB per file         │
    │                                  │
    │  ⚠️ Compress to under 2MB        │
    │     for faster upload            │
    └──────────────────────────────────┘

    Upload → <POST /cases/{id}/documents> → S3 upload
          │
          │  Progress bar shown
          │  ✅ Uploaded
          │  ❌ Failed → Retry button
          ▼
    [All required docs uploaded?] ──NO──→ [Next disabled]
         │ YES
         ▼
    [Tap "Next"] (enabled when all required docs ✓)
          │
          ▼
═══════════════════════════════════════════════════════════════
 STEP 4: REVIEW & SUBMIT
═══════════════════════════════════════════════════════════════

{Step 4 of 4 — Review}

    ┌──────────────────────────────────────────┐
    │  📋 Review Your Application             │
    │                                           │
    │  ▼ Service Details                   [Edit]│
    │    Service: One Person Company              │
    │    State: Delhi | City: New Delhi           │
    │                                           │
    │  ▼ Business Details                    [Edit]│
    │    Company Name: [Filled]                  │
    │    No. of Directors: 1                     │
    │    Capital: ₹1,00,000                       │
    │                                           │
    │  ▼ Documents (5/7 uploaded)            [Edit]│
    │    ✅ Aadhar Card — Verified              │
    │    ✅ PAN Card — Verified                  │
    │    ✅ Passport Photo — Verified            │
    │    ✅ Address Proof — Verified             │
    │    ⏳ NOC — Pending upload                 │
    │                                           │
    │  ▼ Pricing                               │
    │    Service Fee:       ₹29,999             │
    │    Government Fees:   ₹ 5,500 (est.)      │
    │    ─────────────────────────              │
    │    Total:            ₹35,499 (est.)       │
    │                                           │
    │  ⚠️ Govt fees are estimates.              │
    │     Final amount confirmed after review.  │
    │                                           │
    │  [ ] I agree to Terms & Privacy Policy   │
    │                                           │
    └──────────────────────────────────────────┘

    [Tap "Submit Application"]
          │
          ▼
    <POST /cases/{id}/submit>  ──(saves, changes status to 'submitted')──→  Backend
          │
          │  ✅ Case created + submitted
          │  [Notification sent to user]
          │  [Notification sent to admin]
          ▼
    {Case Submission Success Screen}
          │
          ▼
    ┌──────────────────────────────────────────┐
    │           ✅ Application Submitted!       │
    │                                           │
    │    Your Case Number:                      │
    │         LET-2026-00001                    │
    │         [📋 Copy]                         │
    │                                           │
    │    📧 Confirmation sent to:               │
    │       arjun@email.com                     │
    │                                           │
    │    "We'll review your application         │
    │     within 24 hours"                      │
    │                                           │
    │    👤 Assigned Expert:                    │
    │       Dr. Priya Sharma (CA)              │
    │       [Message]  [Call]                   │
    │                                           │
    │    [🏠 Go to Dashboard]                  │
    │    [📋 View Case Details]                 │
    │                                           │
    └──────────────────────────────────────────┘
```

---

## Flow 4: Case Lifecycle (Status Flow)

```
┌─────────────────────────────────────────────────────────────┐
│               CASE STATUS FLOW                                │
└─────────────────────────────────────────────────────────────┘

                    ┌─────────────┐
                    │   DRAFT     │  (Saved but not submitted)
                    └──────┬──────┘
                           │ User submits
                           ▼
                    ┌─────────────┐
            ┌───────│ SUBMITTED   │ User submits application
            │       └──────┬──────┘
            │              │ Admin reviews
            │              ▼
            │       ┌─────────────┐
            │       │ UNDER_REVIEW│ Admin checks documents
            │       └──────┬──────┘
            │              │
            │    ┌─────────┴──────────┐
            │    │                     │
            │    ▼                     ▼
            │ ┌────────────┐    ┌──────────────┐
            │ │  DOCUMENTS │    │  IN_PROGRESS │
            │ │  _PENDING  │    └───────┬───────┘
            │ └────────────┘            │
            │    (Missing/invalid       │
            │     documents)            │ Payment confirmed
            │    [Upload docs]           ▼
            │         │         ┌──────────────┐
            │         │         │  PENDING_    │
            │         │         │  PAYMENT     │
            │         │         └───────┬──────┘
            │         │                 │
            │         │          Payment received
            │         │                 │
            │         │                 ▼
            │         │          ┌──────────────┐
            │         │          │  COMPLETED   │ ✅
            │         │          └──────────────┘
            │         │
            │         └──────┐
            │                │ User cancels
            │                ▼
            │          ┌──────────────┐
            │          │  CANCELLED   │
            │          └──────────────┘
            │
            └──────────────┐ Admin rejects
                           ▼
                    ┌──────────────┐
                    │  REJECTED    │
                    └──────────────┘


┌─────────────────────────────────────────────────────────────┐
│           ADMIN/PROFESSIONAL STATUS UPDATE FLOW              │
└─────────────────────────────────────────────────────────────┘

[Admin opens case from Admin Panel]
          │
          ▼
    {Case Detail — Admin View}
          │
          ▼
    [Change Status dropdown] → Select new status
          │
          ▼
    [Add comment (optional)]
          │
          ▼
    [Confirm Status Change]
          │
          ▼
    <PUT /admin/cases/{id}/status>
          │
          │  → CaseStatusHistory entry created
          │  → Notification sent to user
          │  → Email sent to user (optional)
          │  → Case document auto-updated
          ▼
    [User receives push notification + in-app notification]
          │
          ▼
    {Notification on Home screen}
```

---

## Flow 5: Document Upload & Verification

```
[User opens Case Detail]
          │
          ▼
    [Scrolls to Documents section]
          │
          ▼
    [Tap "Upload More Documents"]
          │
          ▼
    [Select document type from dropdown]
          │
          ▼
    [Choose: Camera / Gallery / Files]
          │
          ▼
    [File selected → Compress if > 2MB]
          │
          ▼
    <POST /cases/{case_id}/documents>
          │
          │  File → FastAPI → S3
          │  Returns: {document_id, file_url, status: "uploaded"}
          │
          ▼
    [Document appears in list: "Uploaded ✓"]
          │
          │  (Professional reviews)
          │
          ▼
    ┌─────────────────────────────────┐
    │ Document Statuses:              │
    │                                 │
    │ ✅ Aadhar Card — Verified      │
    │ ⏳ PAN Card — Under Review     │
    │ ❌ Address Proof — Rejected    │
    │    Reason: "Image too blurry.   │
    │     Please upload a clearer    │
    │     copy with all 4 corners    │
    │     visible."                  │
    │    [Re-upload]                 │
    │                                 │
    └─────────────────────────────────┘

    [If Rejected → User re-uploads]
          │
          │  Status: "rejected" → "uploaded" (new)
          │
          ▼
    [Re-uploaded → Professional re-checks]


ADMIN DOCUMENT VERIFICATION:
    [Admin/Professional opens Document]
          │
          ▼
    [Preview document (image/PDF viewer)]
          │
          ▼
    [Tap: ✓ Verify  OR  ✗ Reject]
          │
          │  [Reject → Enter reason]
          ▼
    <PUT /admin/documents/{id}/verify>
          │
          │  Status updated
          │  User notified: "Address Proof verified!" or
          │                   "Address Proof needs resubmission"
          ▼
    [Case status auto-checks: All required docs verified?
           YES → Status can move to "in_progress"]
```

---

## Flow 6: Messaging / Chat on Case

```
┌─────────────────────────────────────────────────────────────┐
│                   CASE MESSAGING FLOW                        │
└─────────────────────────────────────────────────────────────┘

[User taps "View Messages" on Case Detail]
          │
          ▼
    {Case Chat Screen}
          │
          ▼
    [Load: <GET /cases/{id}/messages?page=1>]
          │
          │  Last 50 messages (paginated)
          │  Unread messages marked
          ▼
    [Message bubbles displayed]
    ┌──────────────────────────────────┐
    │  Case: LET-2026-00001           │
    │  Expert: Dr. Priya Sharma    🟢│
    │  ─────────────────────────────── │
    │                                 │
    │  [System: Case submitted ✅]     │
    │  [Day 1, 10:30 AM]              │
    │                                 │
    │  [User bubble (right, blue)]    │
    │  "Hi, I have a question about   │
    │   the capital requirement."     │
    │  [10:32 AM]                     │
    │                                 │
    │  [Expert bubble (left, white)]  │
    │  "Hi Arjun! Great question.     │
    │   For OPC, the minimum capital  │
    │   is ₹1 lakh, but there's no   │
    │   upper limit."                │
    │  [10:45 AM] ✓✓ (read)          │
    │                                 │
    │  [Document attachment (left)]   │
    │  📄 capital_requirements.pdf   │
    │  [Tap to download]              │
    │  [10:46 AM]                     │
    │                                 │
    │  ┌──────────────────────────┐   │
    │  │ Type a message...        │   │
    │  └──────────────────────────┘ 📎│
    └─────────────────────────────────┘

    [Type message + send]
          │
          ▼
    <POST /cases/{id}/messages>
          │
          │  ✅ Message saved
          │  [Expert receives push notification]
          ▼
    [Message appears with ✓ (sent)]
          │
          │  Expert reads → ✓✓ (read receipt)
          │
          ▼
    [User gets read receipt in real-time]


INTERNAL NOTE (Admin/Professional only):
    [Tap 📎 → "Add Internal Note"]
          │
          ▼
    [Toggle: "Internal (not visible to user)"]
          │
          ▼
    [Type note]
          │
          ▼
    [Send → Only visible to staff]
```

---

## Flow 7: Payment Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    PAYMENT FLOW                              │
└─────────────────────────────────────────────────────────────┘

[Case moves to "Pending Payment" status]
          │
          ▼
    [User receives notification:
     "Payment required for LET-2026-00001"]
          │
          ▼
    {Payment Screen}
    OR
    [User taps "Pay Now" on Case Detail]
          │
          ▼
    ┌──────────────────────────────────────────┐
    │  💳 Payment Summary                      │
    │                                           │
    │  Case: LET-2026-00001                    │
    │  Service: One Person Company Registration │
    │                                           │
    │  ─────────────────────────────────────── │
    │  Service Fee:        ₹29,999             │
    │  Government Fees:    ₹ 5,500             │
    │  ─────────────────────────────────────── │
    │  Total to Pay:       ₹35,499             │
    │                                           │
    │  Payment Method:                           │
    │                                           │
    │  ● UPI (Recommended)          💳          │
    │  ○ Credit / Debit Card     💳           │
    │  ○ Net Banking             💳           │
    │  ○ Wallet (PhonePe/Paytm)  💳           │
    │                                           │
    │  🔒 100% Secure Payment                   │
    │     Powered by Razorpay                   │
    │                                           │
    │  [      PAY ₹35,499      ]                │
    └──────────────────────────────────────────┘

    [Tap "Pay ₹35,499"]
          │
          ▼
    <POST /payments/initiate>
          │
          │  Creates Razorpay order
          │  Returns: razorpay_order_id, amount, currency
          ▼
    [Razorpay checkout opens]
          │
          │  (In-app for Android, In-app/WebView for iOS)
          │
          ▼
    [User completes UPI/Card/NetBanking payment]
          │
          │  ✅ SUCCESS          ❌ FAILED/CANCELLED
          ▼                        ▼
    [Razorpay sends         [User sees error]
     webhook to backend]     Returns to app
          │                   Cancelled order
          ▼                   marked "failed"
    <POST /payments/webhook>
          │
          │  Backend verifies
          │  HMAC signature
          │
          │  Payment verified?
          │   YES → Update DB
          │   Case → in_progress
          │   User → Notification
          │   Expert → Notification
          │   Email receipt sent
          │
          ▼
    [Polling detects success OR
     Webhook triggers real-time update]
          │
          ▼
    {Payment Success Screen}
          │
          ▼
    ┌──────────────────────────────────────────┐
    │         ✅ Payment Successful!           │
    │                                           │
    │  Amount: ₹35,499                         │
    │  Order ID: razorpay_order_XXXX           │
    │  Transaction ID: XXXXXXXXXX              │
    │  Paid on: Apr 27, 2026, 4:30 PM          │
    │                                           │
    │  📧 Receipt sent to arjun@email.com      │
    │                                           │
    │  [Download Receipt]                       │
    │  [View Case]                              │
    └──────────────────────────────────────────┘
```

---

## Flow 8: Notifications (Real-time)

```
┌─────────────────────────────────────────────────────────────┐
│               NOTIFICATION FLOW                              │
└─────────────────────────────────────────────────────────────┘

Trigger Events ──────────────────────────────────────────────→

    ① Case submitted
       → User notification: "Case LET-XXXX submitted!"
       → Admin notification: "New case: LET-XXXX"
       → Expert notification: "New assignment"

    ② Status changes
       → User notification: "Your case status updated to [X]"
       → Email (optional): Case status change email

    ③ Document verified/rejected
       → User notification: "[Document] verified ✓"
       → OR: "[Document] needs resubmission — [reason]"

    ④ New message on case
       → Recipient notification: "[Name]: [message preview...]"

    ⑤ Payment received
       → User notification: "Payment ₹X received ✓"
       → User email: Payment receipt

    ⑥ Case completed
       → User notification: "🎉 Case LET-XXXX completed!"
       → User email: Completion + next steps

    ⑦ Reminder
       → "Submit pending documents for LET-XXXX"
       → Scheduled: 48h after documents_pending status


Notification Types ──────────────────────────────────────────→

    🔔 In-App: Real-time badge update on bell icon
    📧 Email: Immediate or batched (daily digest)
    📱 Push: FCM push notification → device
    💬 SMS: OTP only (for critical alerts — future)


User Notification Center ────────────────────────────────────→

    [Bell icon on Home → Notification List]
          │
          ▼
    ┌──────────────────────────────────────────┐
    │  Notifications          [Mark All Read]  │
    │  ───────────────────────────────────────  │
    │  🔔 Case Update — 2 hours ago            │
    │  Your case LET-2026-00001 has moved to   │
    │  "Under Review" status.                   │
    │                                           │
    │  💳 Payment — Yesterday                   │
    │  Payment of ₹35,499 received for         │
    │  LET-2026-00001. Receipt sent to email.  │
    │                                           │
    │  📄 Document — 2 days ago                 │
    │  Your Aadhar Card has been verified.      │
    │                                           │
    │  [Older notifications collapsed]          │
    └──────────────────────────────────────────┘

    [Tap notification] → Navigate to relevant screen
```

---

## Flow 9: Admin/Professional Case Management

```
[Admin logs into Admin Panel (web dashboard)]
          │
          ▼
    {Admin Dashboard}
          │
          ▼
    ┌──────────────────────────────────────────┐
    │  📊 Today's Overview                      │
    │  New Cases: 12  |  In Progress: 45       │
    │  Pending Docs: 8  |  Completed Today: 3   │
    │                                           │
    │  [View All Cases]  [My Assignments]       │
    └──────────────────────────────────────────┘

    [Click "View All Cases"]
          │
          ▼
    {Cases List — Admin View}
          │
          │  Filters: Status, Category, Date, State, Assigned To
          ▼
    [Click on a Case]
          │
          ▼
    {Full Case Detail — Admin View}
          │
          │  Includes all user data + internal controls
          ▼
    ┌──────────────────────────────────────────┐
    │  LET-2026-00001 — OPC Registration       │
    │  [Client: Arjun Singh]  [Assigned to: Me] │
    │  Status: [Under Review ▼]                 │
    │  ─────────────────────────────────────── │
    │  📋 Form Data (read/edit)                 │
    │  📄 Documents (verify/reject)             │
    │  💬 Messages (user + internal notes)      │
    │  📝 Status History                        │
    │  💰 Payment: ✅ Received ₹35,499         │
    │  ─────────────────────────────────────── │
    │  [Update Status] [Add Note] [Assign]      │
    └──────────────────────────────────────────┘

    [Update Status: Under Review → In Progress]
          │
          ▼
    [Add note: "Documents verified. Proceeding."]  (internal)
          │
          ▼
    [Confirm]
          │
          │  Status history recorded
          │  User notified
          │  Case data saved
          ▼
    [Success: Status updated]
```

---

## Flow 10: Profile & Settings

```
[User taps Profile tab / Avatar on Home]
          │
          ▼
    {Profile Screen}
          │
          ├── [Edit Profile] → Update name, phone
          │
          ├── [Change Password] → Old + New + Confirm
          │
          ├── [Notifications Settings]
          │     ├── Case Updates: [Toggle ON/OFF]
          │     ├── Payments: [Toggle ON/OFF]
          │     └── Promotions: [Toggle ON/OFF]
          │
          ├── [Language] → English / हिंदी
          │
          ├── [Help & Support]
          │     ├── FAQs
          │     ├── Raise Ticket
          │     └── Call Support
          │
          ├── [Legal]
          │     ├── Terms of Service
          │     └── Privacy Policy
          │
          └── [Sign Out]
                ├── Confirmation dialog
                └── → {Login Screen}
```

---

## Error States & Edge Cases

```
EMPTY STATES:

  My Cases empty:
  ┌──────────────────────────────────┐
  │      📋                          │
  │   No cases yet                    │
  │                                  │
  │   Ready to get started?           │
  │   Browse our services and        │
  │   submit your first request.     │
  │                                  │
  │   [Browse Services →]            │
  └──────────────────────────────────┘

  Messages empty:
  ┌──────────────────────────────────┐
  │      💬                          │
  │   No messages yet                │
  │                                  │
  │   Start a conversation with       │
  │   your assigned expert.          │
  │                                  │
  └──────────────────────────────────┘

  Search no results:
  ┌──────────────────────────────────┐
  │   🔍 "Company registration"     │
  │                                  │
  │   No services found.             │
  │   Try different keywords.        │
  └──────────────────────────────────┘


ERROR HANDLING:

  Network error:
  [Show: "Connection error. Check your internet.
          [Retry] [Retry Later]"]

  OTP wrong (3 attempts):
  [Show: "Too many attempts. Try again in 5 minutes."
   Resend button disabled for 5 minutes]

  Payment failed:
  [Show: "Payment failed. Please try again."
   Order preserved, retry within 30 minutes]

  Document upload fails:
  [Show: "Upload failed. Please try again."
   File not lost — tap retry on the same file]
```
