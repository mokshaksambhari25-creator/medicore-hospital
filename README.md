# MediCore Hospital

A working hospital website (public pages + staff console + patient portal).

## How this stays on (no `python3 app.py`)

**GitHub does not run this site.** GitHub is only the folder of code. GitHub Pages cannot do login or a database.

| Place | What it does |
|---|---|
| **This Mac** | Starts by itself when you log in (`LaunchAgent`). Open [http://127.0.0.1:5000](http://127.0.0.1:5000) or double-click `SERVER/OPEN SITE.command`. |
| **GitHub** | Stores the project so you can share and deploy it. |
| **Render** | The **live webpage** on the internet. Render starts Flask. You never type Python. |

## Demo logins

| Role | ID | Password | Then |
|---|---|---|---|
| Staff | `DOC-1001` | `123456` | 6-digit OTP (shown on screen in demo) |
| Patient | `P-4821` | `Aarav21` | same OTP step |
| Admin | `ADMIN-1000` | `Admin24` | same OTP step |

Forgot password is on the login card (demo code on screen until you add Gmail SMTP).

## What is already built

- Home, About, Departments, Facilities, **Book a slot**, Contact, Sign in
- Hindi / English toggle
- OTP login, forgot password
- Public appointment → staff Confirm
- Patient UPI / card / net-banking checkout (demo; Razorpay if you add keys)
- SMS / email / WhatsApp **log** (real send if you add Twilio / SMTP later)

## Put the project on GitHub (you, once)

1. Create a free account: https://github.com/signup  
2. New repository named `medicore-hospital`. **Do not** tick “Add a README”.  
3. Tell me your GitHub username (or the repo URL). I will push this folder.

Until then the site already runs on this Mac.

## Live on the internet (Render, free)

After the GitHub repo exists:

1. Sign up at https://render.com with GitHub.  
2. **New → Web Service** → `medicore-hospital`.  
3. Build: `pip install -r requirements.txt`  
   Start: `gunicorn app:app --bind 0.0.0.0:$PORT`  
4. Env: `MEDICORE_DB=sqlite`, `MEDICORE_HTTPS=1`, `MEDICORE_SECRET` = any long random string.

Render gives `https://….onrender.com`. That URL is the live hospital. No Python on your laptop.

## Optional keys (not required for the site to work)

| Feature | Env vars |
|---|---|
| Real SMS OTP | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM` |
| Real email | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` |
| Real UPI | `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET` |
| Real WhatsApp | `TWILIO_WHATSAPP_FROM` plus Twilio SID/token |

Without these, every flow still works and is labelled **Demo**.
