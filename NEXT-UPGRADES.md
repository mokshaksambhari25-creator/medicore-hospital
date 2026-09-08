# 7 upgrades after this version

These are **not built yet**. Each one can be added on top of the current Flask app. Real SMS, email, WhatsApp and card payments need accounts you own — I cannot send them without those keys.

Today the **Email & SMS** page only **logs a row** in the database. Nobody’s phone or inbox is contacted.

---

## 1. SMS OTP on login

**What:** After the password (or instead of it), a 6-digit code is sent to the patient’s or doctor’s Indian mobile. Sign-in completes only if the code matches.

**Can we do it?** Yes.

**You need:**
- A Twilio account **or** MSG91 (common in India)
- Account SID + Auth Token (Twilio) or Auth key (MSG91)
- A sender ID / phone number approved for India
- Phone numbers already stored on each user (we already have `phone` on patients and doctors)

**How:** Add `/api/login/otp` that creates a short-lived code, SMS it, then `/api/login/verify` checks the code and opens the session. Codes expire in 5 minutes.

---

## 2. Email login / email codes

**What:** A one-time code or magic link is emailed (Gmail, hospital address).

**Can we do it?** Yes.

**You need one of:**
- Gmail address + **App Password** (2-step verification on), or
- SendGrid / Resend API key, or
- Hospital SMTP (host, port, username, password)

**How:** Flask sends mail with that SMTP/API. Same OTP table as #1, delivered by email instead of SMS.

---

## 3. Forgot password

**What:** “Forgot password” on the login card. A reset link or code is sent, user sets a new password.

**Can we do it?** Yes.

**You need:** The same email setup as #2. Without email (or SMS), a reset cannot be proven.

**How:** Token stored hashed, 30-minute expiry, one-use. Admin can still reset a staff password from the console as a fallback.

---

## 4. Book an appointment without signing in

**What:** Public form on Contact / a new Book page: name, phone, department, preferred slot. Staff see it as **Pending** and confirm.

**Can we do it?** Yes. **No extra account.**

**How:** New public POST `/api/public/appointment` writes into the existing `appointments` table with status `Pending`. Optional: send SMS/email confirmation once #1 or #2 is live.

---

## 5. Real UPI / card pay (Razorpay)

**What:** Patient “Pay bill” opens a real Razorpay checkout (UPI, cards, net banking) instead of only marking the invoice Paid in the demo.

**Can we do it?** Yes.

**You need:**
- Razorpay account (business KYC)
- Key ID + Key Secret
- HTTPS live site (Render URL is enough)

**How:** Server creates an order, browser opens Razorpay Checkout, webhook `/api/pay/webhook` marks the invoice **Paid** only after Razorpay confirms.

---

## 6. WhatsApp reminders

**What:** Appointment reminder and “report ready” as a WhatsApp message, not only a log row.

**Can we do it?** Yes.

**You need:**
- Meta WhatsApp Cloud API (business phone + token) **or** Twilio WhatsApp
- Patient must have opted in (Indian DLT / WhatsApp template approval)

**How:** When an appointment is Confirmed or a diagnostic is Done, the server sends the approved template. The Email & SMS page would show **Delivered** only after the provider says so.

---

## 7. Hindi + English site

**What:** A language toggle on every public page and the console (हिन्दी / English).

**Can we do it?** Yes. **No extra account.**

**How:** A small `i18n` dictionary in JS (and matching Flask flash strings). Preference saved in `localStorage`. Medical IDs stay in Latin script (DOC-1001, P-4821).

---

### What I need from you to build any of 1, 2, 3, 5, 6

Tell me which number, then send the matching keys (Twilio / MSG91 / Gmail app password / Razorpay / WhatsApp). I will not put those keys in GitHub.
