"""SMS / email / WhatsApp — live when keys exist, otherwise a demo queue."""
from __future__ import annotations

import os
import smtplib
import urllib.error
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


def _resend_ready() -> bool:
    return bool((os.environ.get("RESEND_API_KEY") or "").strip())


def capabilities() -> dict:
    sms = bool(
        (os.environ.get("TWILIO_ACCOUNT_SID") and os.environ.get("TWILIO_AUTH_TOKEN"))
        or (os.environ.get("MSG91_AUTH_KEY") or "").strip()
    )
    whatsapp = bool(os.environ.get("TWILIO_WHATSAPP_FROM") or os.environ.get("WHATSAPP_TOKEN"))
    razorpay = bool(os.environ.get("RAZORPAY_KEY_ID") and os.environ.get("RAZORPAY_KEY_SECRET"))
    email = _smtp_ready() or _resend_ready()
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


def _resend_send(to: str, subject: str, body: str) -> tuple[bool, str]:
    if not _resend_ready():
        return False, "No RESEND_API_KEY"
    if "@" not in str(to or ""):
        return False, "Need a real email address (not a phone number)."
    import json

    key = (os.environ.get("RESEND_API_KEY") or "").strip()
    frm = (os.environ.get("RESEND_FROM") or "MediCore Hospital <beth.t@example.com>").strip()
    payload = json.dumps({"from": frm, "to": [to], "subject": subject, "text": body}).encode()
    req = urllib.request.Request("https://api.resend.com/emails", data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=12)
        return True, ""
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "ignore")[:280]
        return False, raw or f"Resend HTTP {e.code}"
    except Exception as e:
        return False, str(e)[:200]


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


def _msg91_sms(to: str, body: str) -> bool:
    key = (os.environ.get("MSG91_AUTH_KEY") or "").strip()
    sender = (os.environ.get("MSG91_SENDER") or "MDCORE").strip()[:6]
    digits = "".join(c for c in str(to or "") if c.isdigit())
    if not key or len(digits) < 10:
        return False
    if len(digits) == 10:
        digits = "91" + digits
    data = (
        f"authkey={quote(key)}&mobiles={digits}&message={quote(body)}"
        f"&sender={quote(sender)}&route=4&country=91"
    ).encode()
    req = urllib.request.Request("https://api.msg91.com/api/sendhttp.php", data=data, method="POST")
    try:
        urllib.request.urlopen(req, timeout=12)
        return True
    except Exception:
        return False


def deliver(channel: str, to: str, template: str, body: str) -> dict:
    caps = capabilities()
    sent = False
    err = ""
    ch = (channel or "SMS").upper()
    if ch == "SMS":
        if caps["sms"]:
            sent = _msg91_sms(to, body) or _twilio_sms(to, body)
            if not sent:
                err = "SMS provider rejected the message. Check MSG91 / Twilio."
        else:
            err = "SMS not configured (add MSG91_AUTH_KEY for India)."
    elif ch == "WHATSAPP" and caps["whatsapp"]:
        sent = _twilio_whatsapp(to, body)
        if not sent:
            err = "WhatsApp send failed."
    elif ch == "EMAIL":
        if caps["email"]:
            ok, err = _resend_send(to, f"MediCore · {template}", body)
            sent = ok
            if not sent and _smtp_send(to, f"MediCore · {template}", body):
                sent, err = True, ""
        else:
            err = "Email not configured. Add RESEND_API_KEY on Render."
    status = "Delivered" if sent else ("Failed" if err else "Queued")
    log_alert(to, template, status, "Email" if ch == "EMAIL" else ("WhatsApp" if ch == "WHATSAPP" else "SMS"))
    return {"demo": not sent, "status": status, "channel": ch, "error": err}


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
