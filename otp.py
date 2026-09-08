"""One-time codes for login and password reset."""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash, generate_password_hash

import store as db

OTP_MINUTES = 5


def _ph() -> str:
    return "?" if db.kind() == "sqlite" else "%s"


def issue(uid: str, purpose: str, channel: str) -> dict:
    db.ensure_schema()
    code = f"{secrets.randbelow(1_000_000):06d}"
    oid = secrets.token_hex(16)
    expires = (datetime.utcnow() + timedelta(minutes=OTP_MINUTES)).isoformat()
    con = db.connect()
    cur = con.cursor()
    q = _ph()
    cur.execute(
        f"INSERT INTO otps (id, uid, purpose, channel, code_hash, expires_at, used) "
        f"VALUES ({q}, {q}, {q}, {q}, {q}, {q}, {q})",
        (oid, uid, purpose, channel, generate_password_hash(code, method="pbkdf2:sha256"), expires, 0),
    )
    if db.kind() == "sqlite":
        con.commit()
    cur.close()
    con.close()
    return {"id": oid, "code": code, "expires_at": expires, "channel": channel}


def verify(oid: str, uid: str, purpose: str, code: str) -> tuple[bool, str]:
    db.ensure_schema()
    con = db.connect()
    cur = con.cursor()
    q = _ph()
    cur.execute(
        f"SELECT id, uid, purpose, code_hash, expires_at, used FROM otps WHERE id={q}",
        (oid,),
    )
    row = cur.fetchone()
    if not row:
        cur.close()
        con.close()
        return False, "Code expired. Sign in again."
    rec = dict(row)
    if rec["uid"] != uid or rec["purpose"] != purpose:
        cur.close()
        con.close()
        return False, "Code does not match this sign-in."
    if int(rec["used"] or 0):
        cur.close()
        con.close()
        return False, "That code was already used."
    try:
        exp = datetime.fromisoformat(str(rec["expires_at"]))
    except ValueError:
        exp = datetime.utcnow()
    if datetime.utcnow() > exp:
        cur.close()
        con.close()
        return False, "Code expired. Sign in again."
    if not check_password_hash(rec["code_hash"], str(code or "").strip()):
        cur.close()
        con.close()
        return False, "Wrong code. Try again."
    cur.execute(f"UPDATE otps SET used=1 WHERE id={q}", (oid,))
    if db.kind() == "sqlite":
        con.commit()
    cur.close()
    con.close()
    return True, ""
