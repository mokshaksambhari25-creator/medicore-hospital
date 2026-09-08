"""SMS / email / WhatsApp — real if env keys exist, otherwise demo log."""
from __future__ import annotations

import os
import socket
import ssl
import urllib.request
from datetime import date, datetime
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import quote
import smtplib

import store as db

_SMTP_FILE = Path(__file__).resolve().parent / "SERVER" / "smtp.env"


def load_smtp_env() -> None:
    if not _SMTP_FILE.is_file():
        return
    for line in _SMTP_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ[key.strip()] = val.strip().strip('"').strip("'")


load_smtp_env()


def save_smtp_env(user: str, password: str, sender: str = "") -> None:
    user = (user or "").strip()
    password = (password or "").replace(" ", "").strip()
    sender = (sender or user).strip()
    _SMTP_FILE.parent.mkdir(parents=True, exist_ok=True)
    _SMTP_FILE.write_text(
        "SMTP_HOST=smtp.gmail.com\n"
        "SMTP_PORT=587\n"
        f"SMTP_USER={user}\n"
        f"SMTP_PASSWORD={password}\n"
        f"SMTP_FROM={sender or user}\n",
        encoding="utf-8",
    )
    load_smtp_env()


def capabilities() -> dict:
    sms = bool(
        (os.environ.get("TWILIO_ACCOUNT_SID") and os.environ.get("TWILIO_AUTH_TOKEN"))
        or os.environ.get("MSG91_AUTH_KEY")
    )
    email = bool(
        (os.environ.get("SMTP_HOST") and os.environ.get("SMTP_USER") and os.environ.get("SMTP_PASSWORD"))
        or os.environ.get("RESEND_API_KEY")
    )
    whatsapp = bool(os.environ.get("TWILIO_WHATSAPP_FROM") or os.environ.get("WHATSAPP_TOKEN"))
    razorpay = bool(os.environ.get("RAZORPAY_KEY_ID") and os.environ.get("RAZORPAY_KEY_SECRET"))
    return {
        "sms": sms,
        "email": email,
        "whatsapp": whatsapp,
        "razorpay": razorpay,
        "demo": not email,
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


def _ipv4_socket(host: str, port: int, timeout: float):
    last = None
    for info in socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM):
        sock = socket.socket(info[0], info[1], info[2])
        sock.settimeout(timeout)
        try:
            sock.connect(info[4])
            return sock
        except OSError as exc:
            last = exc
            sock.close()
    raise last or OSError("Network is unreachable")


def _friendly_net_error(exc: BaseException) -> str:
    text = str(exc).lower()
    if any(w in text for w in ("unreachable", "51", "61", "timed out", "timeout", "connection refused", "blocked")):
        if os.environ.get("RENDER"):
            return (
                "The live Render site blocks Gmail SMTP (network unreachable). "
                "Open http://127.0.0.1:5000 on this Mac, save Gmail there, and Mark done / send from the Mac. "
                "That path can reach smtp.gmail.com."
            )
        return (
            "Could not reach Gmail SMTP. Stay on this Mac (http://127.0.0.1:5000), not the Render URL. "
            "Check Wi‑Fi, then Save Gmail again."
        )
    return str(exc)[:180]


def _smtp_email(to: str, subject: str, body: str) -> tuple[bool, str]:
    load_smtp_env()
    host = os.environ.get("SMTP_HOST") or "smtp.gmail.com"
    if not to:
        return False, "Gmail is not saved yet."
    user = os.environ.get("SMTP_USER") or ""
    password = (os.environ.get("SMTP_PASSWORD") or "").replace(" ", "")
    sender = os.environ.get("SMTP_FROM") or user or "reception@medicore.hospital"
    if not user or not password:
        return False, "Gmail address or App Password missing. Save them on Email & SMS first."
    msg = EmailMessage()
    msg["Subject"] = "MediCore · " + (subject or "Hospital message")
    msg["From"] = f"MediCore Hospital <{sender}>"
    msg["To"] = to
    msg.set_content(body or subject or "")
    ctx = ssl.create_default_context()
    errors = []

    def try_587():
        raw = _ipv4_socket(host, 587, 20)
        s = smtplib.SMTP(timeout=20)
        s.sock = raw
        s._host = host
        s.ehlo()
        s.starttls(context=ctx)
        s.ehlo()
        s.login(user, password)
        s.send_message(msg)
        s.quit()

    def try_465():
        raw = _ipv4_socket(host, 465, 20)
        wrapped = ctx.wrap_socket(raw, server_hostname=host)
        s = smtplib.SMTP_SSL(timeout=20)
        s.sock = wrapped
        s._host = host
        s.ehlo()
        s.login(user, password)
        s.send_message(msg)
        s.quit()

    for attempt in (try_587, try_465):
        try:
            attempt()
            return True, ""
        except smtplib.SMTPAuthenticationError:
            return False, "Gmail rejected login. Use the 16-letter App Password, not your normal Gmail password."
        except Exception as exc:
            errors.append(_friendly_net_error(exc))
    return False, errors[-1] if errors else "Could not send mail."


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


def deliver(channel: str, to: str, template: str, body: str) -> dict:
    caps = capabilities()
    sent = False
    err = ""
    ch = (channel or "SMS").upper()
    if ch == "SMS" and caps["sms"]:
        sent = _twilio_sms(to, body)
    elif ch == "EMAIL":
        sent, err = _smtp_email(to, template, body)
    elif ch == "WHATSAPP" and caps["whatsapp"]:
        sent = _twilio_whatsapp(to, body)
    if sent:
        status = "Delivered"
    elif ch == "EMAIL" and err:
        status = "Failed"
    else:
        status = "Queued"
    log_alert(to, template, status, ch.title() if ch != "SMS" else "SMS")
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
