"""SMS / email / WhatsApp — live when keys exist, otherwise a demo queue."""
from __future__ import annotations

import os
import smtplib
import urllib.request
from datetime import date, datetime
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import quote

import store as db

ROOT = Path(__file__).resolve().parent


def _load_smtp_env() -> None:
    path = ROOT / "SERVER" / "smtp.env"
    if not path.is_file():
        return
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
    except Exception:
        pass


_load_smtp_env()


def _smtp_ready() -> bool:
    if os.environ.get("RENDER"):
        return False
    return bool(os.environ.get("SMTP_HOST") and os.environ.get("SMTP_USER") and os.environ.get("SMTP_PASSWORD"))


def capabilities() -> dict:
    sms = bool(
        (os.environ.get("TWILIO_ACCOUNT_SID") and os.environ.get("TWILIO_AUTH_TOKEN"))
        or os.environ.get("MSG91_AUTH_KEY")
    )
    whatsapp = bool(os.environ.get("TWILIO_WHATSAPP_FROM") or os.environ.get("WHATSAPP_TOKEN"))
    razorpay = bool(os.environ.get("RAZORPAY_KEY_ID") and os.environ.get("RAZORPAY_KEY_SECRET"))
    email = _smtp_ready()
    return {
        "sms": sms,
        "email": email,
        "whatsapp": whatsapp,
        "razorpay": razorpay,
        "demo": not (sms or email or whatsapp or razorpay),
        "render": bool(os.environ.get("RENDER")),
    }


def log_alert(to: str, template: str, status: str, channel: str = "SMS") -> None:
    try:
        rows = db.load_store("alerts")
    except Exception:
        rows = []
    label = f"{channel} · {template}" if channel else template
    rows.insert(
        0,
        {
            "id": f"AL-{int(datetime.utcnow().timestamp() * 1000)}",
            "to": to or "—",
            "template": label[:180],
            "time": datetime.now().strftime("%H:%M"),
            "date": date.today().isoformat(),
            "status": status,
        },
    )
    db.save_store("alerts", rows[:80])


def _twilio_sms(to: str, body: str) -> bool:
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    frm = os.environ.get("TWILIO_FROM")
    if not (sid and token and frm):
        return False
    data = f"From={frm}&To={to}&Body={quote(body)}".encode()
    req = urllib.request.Request(
        f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
        data=data,
        method="POST",
    )
    import base64

    auth = base64.b64encode(f"{sid}:{token}".encode()).decode()
    req.add_header("Authorization", f"Basic {auth}")
    try:
        urllib.request.urlopen(req, timeout=8)
        return True
    except Exception:
        return False


def _twilio_whatsapp(to: str, body: str) -> bool:
    frm = os.environ.get("TWILIO_WHATSAPP_FROM")
    if not frm:
        return False
    dest = to if to.startswith("whatsapp:") else f"whatsapp:{to}"
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    if not (sid and token):
        return False
    data = f"From={frm}&To={dest}&Body={quote(body)}".encode()
    req = urllib.request.Request(
        f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
        data=data,
        method="POST",
    )
    import base64

    auth = base64.b64encode(f"{sid}:{token}".encode()).decode()
    req.add_header("Authorization", f"Basic {auth}")
    try:
        urllib.request.urlopen(req, timeout=8)
        return True
    except Exception:
        return False


def _smtp_send(to: str, subject: str, body: str) -> bool:
    if not _smtp_ready() or "@" not in str(to or ""):
        return False
    host = os.environ.get("SMTP_HOST") or ""
    port = int(os.environ.get("SMTP_PORT") or "587")
    user = os.environ.get("SMTP_USER") or ""
    password = os.environ.get("SMTP_PASSWORD") or ""
    frm = os.environ.get("SMTP_FROM") or user
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = frm
    msg["To"] = to
    msg.set_content(body)
    try:
        with smtplib.SMTP(host, port, timeout=12) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(msg)
        return True
    except Exception:
        return False


def deliver(channel: str, to: str, template: str, body: str) -> dict:
    caps = capabilities()
    sent = False
    ch = (channel or "SMS").upper()
    if ch == "SMS" and caps["sms"]:
        sent = _twilio_sms(to, body)
    elif ch == "WHATSAPP" and caps["whatsapp"]:
        sent = _twilio_whatsapp(to, body)
    elif ch == "EMAIL" and caps["email"]:
        sent = _smtp_send(to, f"MediCore · {template}", body)
    status = "Delivered" if sent else "Queued"
    log_alert(to, template, status, ch.title() if ch != "SMS" else "SMS")
    return {"demo": not sent, "status": status, "channel": ch, "error": ""}


def on_store_change(name: str, prev: list, payload: list) -> None:
    old = {str(r.get("id")): r for r in (prev or [])}
    for row in payload or []:
        rid = str(row.get("id") or "")
        before = old.get(rid) or {}
        st = str(row.get("status") or "")
        phone = str(row.get("phone") or "")
        who = str(row.get("patient") or row.get("patientId") or phone)
        if name == "appointments" and st == "Confirmed" and before.get("status") != "Confirmed":
            body = f"MediCore: appointment confirmed for {row.get('date')} {row.get('time')}."
            deliver("WHATSAPP", phone or who, "Appointment reminder", body)
            deliver("SMS", phone or who, "Appointment reminder", body)
        if name == "diagnostics" and st == "Done" and before.get("status") != "Done":
            body = f"MediCore: your {row.get('test')} report is ready."
            deliver("WHATSAPP", who, "Report ready", body)
            deliver("SMS", phone or who, "Report ready", body)
