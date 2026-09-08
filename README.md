# MediCore Hospital

Flask hospital site: public pages, staff console, patient portal, live database.

GitHub holds the **code**. GitHub Pages **cannot** run this app (no Flask, no database). The live webpage is a host such as **Render**.

## Run on this Mac (no manual MySQL)

```bash
cd ~/Desktop/MediCore-Pages
python3 app.py
```

Open http://127.0.0.1:5000

If MySQL is already running with the old `medicore` user, the app uses it. If not, it creates `medicore-live.db` (SQLite) and still works.

## Demo logins

| Role | ID | Password |
|---|---|---|
| Staff | `DOC-1001` | `123456` |
| Patient | `P-4821` | `Aarav21` |
| Admin | `ADMIN-1000` | `Admin24` |

## Put it on GitHub

1. Create a GitHub account if you do not have one.
2. On github.com click **New repository** (name e.g. `medicore-hospital`). Do not add a README there.
3. In Terminal:

```bash
cd ~/Desktop/MediCore-Pages
git init
git add .
git commit -m "MediCore hospital site"
git branch -M main
git remote add origin https://github.com/YOUR_USER/medicore-hospital.git
git push -u origin main
```

Replace `YOUR_USER` with your GitHub username.

## Live webpage (Render, free)

1. Sign up at https://render.com with the same GitHub account.
2. **New + → Web Service →** select `medicore-hospital`.
3. Runtime: Python. Build: `pip install -r requirements.txt`. Start: `gunicorn app:app --bind 0.0.0.0:$PORT`.
4. Add env vars: `MEDICORE_DB=sqlite`, `MEDICORE_HTTPS=1`, `MEDICORE_SECRET` = any long random string.
5. Deploy. Render gives a URL like `https://medicore-hospital.onrender.com`.

The site stays up. You do not double-click anything. Free instances may sleep after idle; the first visit can take ~30 seconds to wake.

To keep data across deploys, add a Render disk and set `DATABASE_PATH=/data/medicore.db`.

`render.yaml` in this folder does the same wiring if you use Render Blueprint.

## Local MySQL (optional)

Double-click `SERVER/START SERVER AND DATABASE.command` if you still want Sequel Ace / TablePlus on this Mac. Not required for the website.

## Pages

Public: Home, About, Departments, Facilities, Contact, Sign in.

After login: Dashboard, Patients, Doctors, Appointments, Pharmacy, Wards, Diagnostics, Payments, Reports, Email & SMS, Patient portal.
