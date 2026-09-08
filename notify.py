"""SMS / email / WhatsApp — demo queue (no live Gmail SMTP)."""
from __future__ import annotations

import os
import urllib.request
from datetime import date, datetime
from urllib.parse import quote

import store as db


def capabilities() -> dict:
    sms = bool(
        (os.environ.get("TWILIO_ACCOUNT_SID") and os.environ.get("TWILIO_AUTH_TOKEN"))
        or os.environ.get("MSG91_AUTH_KEY")
    )
    whatsapp = bool(os.environ.get("TWILIO_WHATSAPP_FROM") or os.environ.get("WHATSAPP_TOKEN"))
    razorpay = bool(os.environ.get("RAZORPAY_KEY_ID") and os.environ.get("RAZORPAY_KEY_SECRET"))
    return {
        "sms": sms,
        "email": False,
        "whatsapp": whatsapp,
        "razorpay": razorpay,
        "demo": True,
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


def deliver(channel: str, to: str, template: str, body: str) -> dict:
    caps = capabilities()
    sent = False
    ch = (channel or "SMS").upper()
    if ch == "SMS" and caps["sms"]:
        sent = _twilio_sms(to, body)
    elif ch == "WHATSAPP" and caps["whatsapp"]:
        sent = _twilio_whatsapp(to, body)
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
