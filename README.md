# MediCore Hospital

Working hospital website. **GitHub stores the code. Render runs it live. This Mac also runs it at login.**

GitHub: https://github.com/mokshaksambhari25-creator/medicore-hospital

## You do not add Python yourself

- **This Mac:** Python is already installed. The site starts at login. Open http://127.0.0.1:5000 or `SERVER/OPEN SITE.command`.
- **Render:** Render installs Python from `runtime.txt` and packages from `requirements.txt`. You never upload a Python installer. You never start MySQL there.

Database on Render = SQLite file the app creates on first boot (`MEDICORE_DB=sqlite`).

## OTP (works without Twilio)

1. Sign in with ID + password.
2. A **6-digit code appears on the card and is filled in for you**.
3. Click **Verify code**.

Demo logins: `DOC-1001` / `123456` · `P-4821` / `Aarav21` · `ADMIN-1000` / `Admin24`.

## Push to GitHub (once)

Repo already exists. In **GitHub Desktop**: File → Add Local Repository → `~/Desktop/MediCore-Pages` → **Publish / Push origin**.

Or Terminal (will ask you to sign in):

```bash
cd ~/Desktop/MediCore-Pages
git push -u origin main
```

## Live on the internet — Render (you click this)

Do **not** add a Python file or a MySQL server.

1. https://render.com → **Sign up with GitHub** (mokshaksambhari25-creator).
2. **New + → Web Service**.
3. Connect `medicore-hospital`.
4. If Render is set to **Docker** (this caused `open Dockerfile: no such file`): the repo now has a `Dockerfile`. Save, then **Manual Deploy → Clear build cache & deploy**.
   If you prefer **Python** instead: Environment Python · Build `pip install -r requirements.txt` · Start `gunicorn app:app --bind 0.0.0.0:$PORT`
5. **Environment** (Add):
   - `MEDICORE_DB` = `sqlite`
   - `MEDICORE_HTTPS` = `1`
   - `MEDICORE_SECRET` = any long random string (example: `MediCoreLiveSecret2026`)
6. **Create Web Service**. Wait until the status is Live.
7. Open the URL Render shows, e.g. `https://medicore-hospital.onrender.com`.

Free Render sleeps after idle; first open can take ~30 seconds. Then login + OTP + book + pay work like this Mac.

Files Render uses from GitHub: `Dockerfile`, `app.py`, `requirements.txt`, `Procfile`, `render.yaml`, `runtime.txt`.
