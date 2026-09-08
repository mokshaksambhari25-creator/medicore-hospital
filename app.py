#!/usr/bin/env python3
"""
MediCore — Flask + MySQL or SQLite
Run:  python3 app.py
Open: http://127.0.0.1:5000
"""
from __future__ import annotations

import os
import re
import secrets
from datetime import date, datetime, timedelta
from functools import wraps

from flask import Flask, jsonify, request, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash

from logins import (
    ADMIN_ID,
    ADMIN_NAME,
    ADMIN_PASSWORD,
    SEED_STAFF,
    STAFF_PASSWORD,
    name_to_seed_id,
    patient_password,
)
import store as mysql_db
from mysql_cfg import STORE_FIELDS

ROOT = os.path.dirname(os.path.abspath(__file__))
STORES = tuple(STORE_FIELDS.keys())

app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get("MEDICORE_SECRET") or secrets.token_hex(32)
_HTTPS = bool(os.environ.get("RENDER") or os.environ.get("MEDICORE_HTTPS"))
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_NAME="medicore_sid",
    SESSION_COOKIE_SECURE=_HTTPS,
    PREFERRED_URL_SCHEME="https" if _HTTPS else "http",
)

_LOCK = {}
LOCK_LIMIT = 5
LOCK_MINUTES = 2


def today():
    return date.today().isoformat()


def hash_pw(plain: str) -> str:
    return generate_password_hash(plain, method="pbkdf2:sha256")


def seed_payloads():
    t = today()
    return {
        "doctors": [
            {"id": "DOC-1001", "name": "Dr. Meera Nair", "department": "Cardiology", "phone": "+91 98200 11001", "available": True, "login": True},
            {"id": "DOC-1002", "name": "Dr. Rohan Das", "department": "General Medicine", "phone": "+91 98200 11002", "available": True, "login": True},
            {"id": "DOC-1003", "name": "Dr. Kavya Iyer", "department": "Orthopaedics", "phone": "+91 98200 11003", "available": True, "login": True},
            {"id": "DOC-1004", "name": "Dr. Imran Sheikh", "department": "Neurology", "phone": "+91 98200 11004", "available": True, "login": True},
            {"id": "DOC-1005", "name": "Dr. Ananya Bose", "department": "Paediatrics", "phone": "+91 98200 11005", "available": True, "login": True},
            {"id": "DOC-1006", "name": "Dr. Arjun Menon", "department": "Oncology", "phone": "+91 98200 11006", "available": True, "login": True},
        ],
        "patients": [
            {"id": "P-4821", "name": "Aarav Sharma", "age": 42, "gender": "Male", "phone": "+91 98200 11223", "blood": "B+", "department": "Cardiology", "doctorId": "DOC-1001", "status": "Admitted", "ward": "PR-210"},
            {"id": "P-3304", "name": "Ritu Verma", "age": 51, "gender": "Female", "phone": "+91 98330 45671", "blood": "O+", "department": "Oncology", "doctorId": "DOC-1006", "status": "Admitted", "ward": "ICU-01"},
            {"id": "P-7718", "name": "Nikhil Patil", "age": 36, "gender": "Male", "phone": "+91 90045 77812", "blood": "A+", "department": "Orthopaedics", "doctorId": "DOC-1003", "status": "Discharged", "ward": ""},
            {"id": "P-2196", "name": "Sneha Patil", "age": 29, "gender": "Female", "phone": "+91 99870 22114", "blood": "AB+", "department": "Neurology", "doctorId": "DOC-1004", "status": "Observation", "ward": ""},
            {"id": "P-6402", "name": "Fatima Khan", "age": 31, "gender": "Female", "phone": "+91 98111 33445", "blood": "B+", "department": "Maternity", "doctorId": "DOC-1002", "status": "Admitted", "ward": "MT-305"},
            {"id": "P-5580", "name": "Kabir Reddy", "age": 8, "gender": "Male", "phone": "+91 98765 43210", "blood": "O+", "department": "Paediatrics", "doctorId": "DOC-1005", "status": "Admitted", "ward": ""},
        ],
        "appointments": [
            {"id": "AP-5512", "patient": "Aarav Sharma", "patientId": "P-4821", "phone": "+91 98200 11223", "doctorId": "DOC-1001", "department": "Cardiology", "date": t, "time": "09:30 AM", "status": "Confirmed"},
            {"id": "AP-5513", "patient": "Fatima Khan", "patientId": "P-6402", "phone": "+91 98111 33445", "doctorId": "DOC-1002", "department": "Maternity", "date": t, "time": "10:15 AM", "status": "Checked-in"},
            {"id": "AP-5514", "patient": "Nikhil Patil", "patientId": "P-7718", "phone": "+91 90045 77812", "doctorId": "DOC-1003", "department": "Orthopaedics", "date": t, "time": "11:00 AM", "status": "Pending"},
            {"id": "AP-5515", "patient": "Sneha Patil", "patientId": "P-2196", "phone": "+91 99870 22114", "doctorId": "DOC-1004", "department": "Neurology", "date": t, "time": "12:30 PM", "status": "Confirmed"},
            {"id": "AP-5516", "patient": "Kabir Reddy", "patientId": "P-5580", "phone": "+91 98765 43210", "doctorId": "DOC-1005", "department": "Paediatrics", "date": t, "time": "02:00 PM", "status": "Cancelled"},
        ],
        "pharmacy": [
            {"id": "RX-01", "name": "Paracetamol 500mg", "batch": "B-8821", "stock": 420, "min": 80, "unit": "strip"},
            {"id": "RX-02", "name": "Amoxicillin 250mg", "batch": "B-7740", "stock": 64, "min": 60, "unit": "strip"},
            {"id": "RX-03", "name": "Insulin Glargine", "batch": "B-3302", "stock": 18, "min": 25, "unit": "vial"},
            {"id": "RX-04", "name": "ORS sachets", "batch": "B-1190", "stock": 210, "min": 50, "unit": "box"},
            {"id": "RX-05", "name": "Atorvastatin 10mg", "batch": "B-5518", "stock": 90, "min": 40, "unit": "strip"},
        ],
        "rooms": [
            {"id": "ICU-01", "type": "ICU", "floor": "3rd", "beds": 1, "occupied": 1, "tariff": 12000, "occupant": "Ritu Verma", "status": "Occupied", "patients": ["Ritu Verma"]},
            {"id": "ICU-02", "type": "ICU", "floor": "3rd", "beds": 1, "occupied": 0, "tariff": 12000, "occupant": "", "status": "Available", "patients": []},
            {"id": "GW-104", "type": "General Ward", "floor": "1st", "beds": 6, "occupied": 4, "tariff": 1800, "occupant": "4 patients", "status": "Partially Full", "patients": ["Kiran Rao", "Mehul Shah", "Anita Das", "Vikram Iyer"]},
            {"id": "PR-210", "type": "Private", "floor": "2nd", "beds": 1, "occupied": 1, "tariff": 6500, "occupant": "Aarav Sharma", "status": "Occupied", "patients": ["Aarav Sharma"]},
            {"id": "PR-211", "type": "Private", "floor": "2nd", "beds": 1, "occupied": 0, "tariff": 6500, "occupant": "", "status": "Cleaning", "patients": []},
            {"id": "MT-305", "type": "Maternity", "floor": "3rd", "beds": 2, "occupied": 1, "tariff": 4200, "occupant": "Fatima Khan", "status": "Partially Full", "patients": ["Fatima Khan"]},
            {"id": "GW-108", "type": "General Ward", "floor": "1st", "beds": 6, "occupied": 0, "tariff": 1800, "occupant": "", "status": "Available", "patients": []},
            {"id": "PR-214", "type": "Private", "floor": "2nd", "beds": 1, "occupied": 0, "tariff": 6500, "occupant": "", "status": "Available", "patients": []},
        ],
        "invoices": [
            {"id": "INV-77120", "patient": "Aarav Sharma", "patientId": "P-4821", "department": "Cardiology", "amount": 42300, "method": "UPI", "date": "2026-08-16", "status": "Paid", "notes": ""},
            {"id": "INV-77121", "patient": "Ritu Verma", "patientId": "P-3304", "department": "Oncology", "amount": 186500, "method": "Insurance", "date": "2026-08-16", "status": "Processing", "notes": "Claim #ONC-441"},
            {"id": "INV-77122", "patient": "Nikhil Patil", "patientId": "P-7718", "department": "Orthopaedics", "amount": 78900, "method": "Card", "date": "2026-08-15", "status": "Paid", "notes": ""},
            {"id": "INV-77123", "patient": "Sneha Patil", "patientId": "P-2196", "department": "Neurology", "amount": 22150, "method": "Cash", "date": "2026-08-15", "status": "Due", "notes": ""},
            {"id": "INV-77124", "patient": "Fatima Khan", "patientId": "P-6402", "department": "Maternity", "amount": 56000, "method": "Insurance", "date": "2026-08-14", "status": "Paid", "notes": ""},
        ],
        "diagnostics": [
            {"id": "DX-2201", "patient": "Aarav Sharma", "patientId": "P-4821", "test": "ECG", "slot": "09:00 AM", "date": t, "status": "Done"},
            {"id": "DX-2202", "patient": "Ritu Verma", "patientId": "P-3304", "test": "CT Chest", "slot": "11:30 AM", "date": t, "status": "Scheduled"},
            {"id": "DX-2203", "patient": "Sneha Patil", "patientId": "P-2196", "test": "MRI Brain", "slot": "02:00 PM", "date": t, "status": "Scheduled"},
            {"id": "DX-2204", "patient": "Nikhil Patil", "patientId": "P-7718", "test": "X-Ray Knee", "slot": "04:00 PM", "date": t, "status": "Done"},
        ],
        "alerts": [
            {"id": "AL-1", "to": "+91 98200 11223", "template": "Appointment Reminder", "time": "08:10", "date": t, "status": "Delivered"},
            {"id": "AL-2", "to": "+91 98330 45671", "template": "Scan Slot Changed", "time": "08:42", "date": t, "status": "Delivered"},
            {"id": "AL-3", "to": "+91 90045 77812", "template": "Payment Due", "time": "09:05", "date": t, "status": "Failed"},
            {"id": "AL-4", "to": "+91 99870 22114", "template": "Report Ready", "time": "09:31", "date": t, "status": "Queued"},
        ],
    }


def alloc_patient_id(used: set[str]) -> str:
    while True:
        pid = f"P-{secrets.randbelow(9000) + 1000}"
        if pid not in used:
            return pid


def upsert_user(uid: str, password: str, role: str) -> None:
    mysql_db.upsert_user(uid, hash_pw(password), role, replace_hash=False)


def find_patient(pid: str):
    pid = str(pid or "").strip().upper()
    for p in load_store("patients"):
        if str(p.get("id") or "").upper() == pid:
            return p
    return None


def belongs_to_patient(row: dict, pid: str, name: str) -> bool:
    if str(row.get("patientId") or "").upper() == pid:
        return True
    return bool(name) and str(row.get("patient") or "").strip().lower() == name.strip().lower()


def migrate_patient_ids() -> None:
    patients = load_store("patients")
    if not patients:
        return
    seed_map = name_to_seed_id()
    used = {str(p.get("id") or "") for p in patients if str(p.get("id") or "").startswith("P-")}
    used |= mysql_db.user_ids()
    id_map: dict[str, str] = {}
    name_map: dict[str, str] = {}
    changed = False
    for p in patients:
        old = str(p.get("id") or "")
        name = str(p.get("name") or "").strip()
        if re.fullmatch(r"P-\d{4}", old):
            new_id = old
        else:
            candidate = seed_map.get(name)
            if candidate and candidate not in used:
                new_id = candidate
            else:
                new_id = alloc_patient_id(used)
            p["id"] = new_id
            changed = True
        used.add(new_id)
        if old:
            id_map[old] = new_id
        if name:
            name_map[name.lower()] = new_id
        upsert_user(new_id, patient_password(name, new_id), "patient")

    if changed:
        save_store("patients", patients)

    for store_name in ("appointments", "invoices", "diagnostics"):
        items = load_store(store_name)
        dirty = False
        for item in items:
            pid = str(item.get("patientId") or "")
            pname = str(item.get("patient") or "").strip()
            if re.fullmatch(r"P-\d{4}", pid):
                continue
            mapped = id_map.get(pid) or name_map.get(pname.lower())
            if mapped:
                item["patientId"] = mapped
                dirty = True
        if dirty:
            save_store(store_name, items)


def init_db():
    mysql_db.ensure_schema()
    if mysql_db.users_empty():
        for sid in SEED_STAFF:
            mysql_db.upsert_user(sid, hash_pw(STAFF_PASSWORD), "staff", replace_hash=True)
    mysql_db.set_role_patterns()
    if not mysql_db.get_user(ADMIN_ID):
        mysql_db.upsert_user(ADMIN_ID, hash_pw(ADMIN_PASSWORD), "admin", replace_hash=True)
    else:
        mysql_db.upsert_user(ADMIN_ID, hash_pw(ADMIN_PASSWORD), "admin", replace_hash=False)

    payloads = seed_payloads()
    for name in STORES:
        if mysql_db.store_empty(name):
            save_store(name, payloads[name])

    migrate_patient_ids()


def load_store(name):
    return mysql_db.load_store(name)


def save_store(name, payload):
    mysql_db.save_store(name, payload)


def doctor_public(doc_id):
    for d in load_store("doctors"):
        if d.get("id") == doc_id:
            return {
                "id": d["id"],
                "name": d.get("name"),
                "department": d.get("department"),
                "role": "staff",
            }
    return {"id": doc_id, "name": doc_id, "department": "", "role": "staff"}


def current_user():
    uid = session.get("uid")
    role = session.get("role")
    if not uid:
        return None
    if role == "admin":
        return {"id": uid, "name": ADMIN_NAME, "department": "Administration", "role": "admin"}
    if role == "patient":
        p = find_patient(uid) or {}
        return {
            "id": uid,
            "name": p.get("name") or uid,
            "department": p.get("department") or "",
            "role": "patient",
        }
    return doctor_public(uid)


def login_required(fn):
    @wraps(fn)
    def wrap(*args, **kwargs):
        if not session.get("uid"):
            return jsonify({"ok": False, "error": "Sign in required."}), 401
        return fn(*args, **kwargs)

    return wrap


def staff_required(fn):
    @wraps(fn)
    def wrap(*args, **kwargs):
        if not session.get("uid"):
            return jsonify({"ok": False, "error": "Sign in required."}), 401
        if session.get("role") not in ("staff", "admin"):
            return jsonify({"ok": False, "error": "Staff access required."}), 403
        return fn(*args, **kwargs)

    return wrap


def patient_required(fn):
    @wraps(fn)
    def wrap(*args, **kwargs):
        if not session.get("uid") or session.get("role") != "patient":
            return jsonify({"ok": False, "error": "Patient sign in required."}), 401
        return fn(*args, **kwargs)

    return wrap


@app.post("/api/login")
def api_login():
    data = request.get_json(silent=True) or {}
    login_id = str(data.get("id") or "").strip().upper()
    password = str(data.get("password") or "")
    wanted = str(data.get("role") or "staff").strip().lower()
    if wanted not in ("staff", "patient", "admin"):
        wanted = "staff"
    now = datetime.utcnow()
    lock = _LOCK.get(login_id)
    if lock and lock.get("until") and now < lock["until"]:
        return jsonify({"ok": False, "error": "Too many attempts. Try again later."}), 429

    labels = {
        "staff": "Invalid staff ID or password",
        "patient": "Invalid patient ID or password",
        "admin": "Invalid admin ID or password",
    }
    generic = labels[wanted]
    row = mysql_db.get_user(login_id)
    role = (row["role"] if row else "") or ""
    if not row or role != wanted or not check_password_hash(row["password_hash"], password):
        rec = _LOCK.get(login_id) or {"n": 0, "until": None}
        rec["n"] = rec["n"] + 1
        if rec["n"] >= LOCK_LIMIT:
            rec["until"] = now + timedelta(minutes=LOCK_MINUTES)
            rec["n"] = 0
        _LOCK[login_id] = rec
        if row and role and role != wanted:
            return jsonify(
                {"ok": False, "error": "This ID belongs to a different sign-in type. Choose the matching tab."}
            ), 401
        return jsonify({"ok": False, "error": generic}), 401

    _LOCK.pop(login_id, None)
    session.clear()
    session["uid"] = row["id"]
    session["role"] = role
    session.permanent = True
    return jsonify({"ok": True, "user": current_user()})


@app.post("/api/logout")
def api_logout():
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/health")
def api_health():
    return jsonify({"ok": True, "db": mysql_db.kind()})


@app.get("/api/me")
def api_me():
    user = current_user()
    if not user:
        return jsonify({"ok": False, "user": None}), 200
    return jsonify({"ok": True, "user": user})


@app.get("/api/bootstrap")
@staff_required
def api_bootstrap():
    payload = {name: load_store(name) for name in STORES}
    payload["user"] = current_user()
    return jsonify({"ok": True, "data": payload})


@app.get("/api/store/<name>")
@staff_required
def api_get_store(name):
    if name not in STORES:
        return jsonify({"ok": False, "error": "Unknown store"}), 404
    return jsonify(load_store(name))


@app.put("/api/store/<name>")
@staff_required
def api_put_store(name):
    if name not in STORES:
        return jsonify({"ok": False, "error": "Unknown store"}), 404
    body = request.get_json(silent=True)
    if not isinstance(body, list):
        return jsonify({"ok": False, "error": "Expected a list"}), 400
    save_store(name, body)
    return jsonify({"ok": True})


@app.get("/api/patient/home")
@patient_required
def api_patient_home():
    pid = session.get("uid")
    patient = find_patient(pid)
    if not patient:
        return jsonify({"ok": False, "error": "Patient record not found."}), 404
    name = patient.get("name") or ""
    doctors = load_store("doctors")
    doctor = next((d for d in doctors if d.get("id") == patient.get("doctorId")), None)
    invoices = [x for x in load_store("invoices") if belongs_to_patient(x, pid, name)]
    diagnostics = [x for x in load_store("diagnostics") if belongs_to_patient(x, pid, name)]
    appointments = [x for x in load_store("appointments") if belongs_to_patient(x, pid, name)]
    return jsonify(
        {
            "ok": True,
            "user": current_user(),
            "patient": patient,
            "doctor": {
                "id": (doctor or {}).get("id"),
                "name": (doctor or {}).get("name") or patient.get("doctorId") or "—",
                "department": (doctor or {}).get("department") or patient.get("department") or "",
            },
            "invoices": invoices,
            "diagnostics": diagnostics,
            "appointments": appointments,
        }
    )


@app.post("/api/patient/pay")
@patient_required
def api_patient_pay():
    data = request.get_json(silent=True) or {}
    invoice_id = str(data.get("invoiceId") or "").strip()
    method = str(data.get("method") or "UPI").strip() or "UPI"
    pid = session.get("uid")
    patient = find_patient(pid)
    if not patient:
        return jsonify({"ok": False, "error": "Patient record not found."}), 404
    name = patient.get("name") or ""
    invoices = load_store("invoices")
    found = None
    for inv in invoices:
        if inv.get("id") == invoice_id and belongs_to_patient(inv, pid, name):
            found = inv
            break
    if not found:
        return jsonify({"ok": False, "error": "Invoice not found."}), 404
    if found.get("status") == "Paid":
        return jsonify({"ok": True, "invoice": found})
    found["status"] = "Paid"
    found["method"] = method
    found["date"] = today()
    found["patientId"] = pid
    save_store("invoices", invoices)
    alerts = load_store("alerts")
    alerts.insert(
        0,
        {
            "id": f"AL-{int(datetime.utcnow().timestamp() * 1000)}",
            "to": patient.get("phone") or name,
            "template": "Payment receipt",
            "time": datetime.now().strftime("%H:%M"),
            "date": today(),
            "status": "Queued",
        },
    )
    save_store("alerts", alerts[:80])
    return jsonify({"ok": True, "invoice": found})


@app.post("/api/patients")
@staff_required
def api_create_patient():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name") or "").strip()
    if not name:
        return jsonify({"ok": False, "error": "Name is required."}), 400
    patients = load_store("patients")
    used = {str(p.get("id") or "") for p in patients} | mysql_db.user_ids()
    pid = alloc_patient_id(used)
    password = patient_password(name, pid)
    row = {
        "id": pid,
        "name": name,
        "age": int(data.get("age") or 0),
        "gender": str(data.get("gender") or "Other"),
        "phone": str(data.get("phone") or "").strip(),
        "blood": str(data.get("blood") or "—").strip() or "—",
        "department": str(data.get("department") or "General Medicine"),
        "doctorId": str(data.get("doctorId") or ""),
        "status": str(data.get("status") or "Observation"),
        "ward": "",
    }
    patients.insert(0, row)
    save_store("patients", patients)
    upsert_user(pid, password, "patient")
    return jsonify({"ok": True, "patient": row, "password": password})


@app.post("/api/staff-login")
@staff_required
def api_staff_login_add():
    data = request.get_json(silent=True) or {}
    sid = str(data.get("id") or "").strip().upper()
    if not sid.startswith("DOC-"):
        return jsonify({"ok": False, "error": "Invalid staff ID"}), 400
    if mysql_db.get_user(sid):
        mysql_db.upsert_user(sid, hash_pw(STAFF_PASSWORD), "staff", replace_hash=False)
        return jsonify({"ok": True, "id": sid})
    mysql_db.upsert_user(sid, hash_pw(STAFF_PASSWORD), "staff", replace_hash=True)
    return jsonify({"ok": True, "id": sid})


@app.delete("/api/staff-login/<sid>")
@staff_required
def api_staff_login_delete(sid):
    sid = str(sid or "").strip().upper()
    if session.get("uid") == sid:
        return jsonify({"ok": False, "error": "You cannot remove your own login."}), 400
    if mysql_db.count_role("staff") <= 1:
        return jsonify({"ok": False, "error": "Keep at least one staff login."}), 400
    mysql_db.delete_user(sid, role="staff")
    return jsonify({"ok": True})


@app.route("/")
def index():
    return send_from_directory(ROOT, "index.html")


@app.route("/<path:path>")
def public_file(path):
    lower = path.lower()
    if (
        path.startswith("api/")
        or path.startswith("BACKUP/")
        or path.startswith("SERVER/")
        or path.startswith(".")
        or lower.endswith(".py")
        or lower.endswith(".db")
        or lower.endswith(".env")
        or lower.endswith(".command")
        or lower.endswith(".sh")
        or lower.endswith(".pid")
        or lower.endswith(".log")
        or path.endswith("MediCore-Login-IDs.pdf")
    ):
        return jsonify({"error": "Not found"}), 404
    full = os.path.join(ROOT, path)
    if os.path.isfile(full):
        return send_from_directory(ROOT, path)
    return send_from_directory(ROOT, "index.html")


init_db()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    print(f"MediCore  →  http://{host}:{port}  ({mysql_db.kind()})")
    app.run(host=host, port=port, debug=False)
