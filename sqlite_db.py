"""SQLite storage — same function names as mysql_db so the app can boot without MySQL."""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

from mysql_cfg import (
    BOOL_FIELDS,
    FLOAT_FIELDS,
    INT_FIELDS,
    JSON_FIELDS,
    STORE_FIELDS,
)

ROOT = Path(__file__).resolve().parent
STORES = tuple(STORE_FIELDS.keys())

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'staff'
);
CREATE TABLE IF NOT EXISTS doctors (
  pos INTEGER NOT NULL,
  id TEXT PRIMARY KEY,
  name TEXT,
  department TEXT,
  phone TEXT,
  available INTEGER NOT NULL DEFAULT 1,
  login INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS patients (
  pos INTEGER NOT NULL,
  id TEXT PRIMARY KEY,
  name TEXT,
  age INTEGER,
  gender TEXT,
  phone TEXT,
  blood TEXT,
  department TEXT,
  doctorId TEXT,
  status TEXT,
  ward TEXT
);
CREATE TABLE IF NOT EXISTS appointments (
  pos INTEGER NOT NULL,
  id TEXT PRIMARY KEY,
  patient TEXT,
  patientId TEXT,
  phone TEXT,
  doctorId TEXT,
  department TEXT,
  date TEXT,
  time TEXT,
  status TEXT
);
CREATE TABLE IF NOT EXISTS pharmacy (
  pos INTEGER NOT NULL,
  id TEXT PRIMARY KEY,
  name TEXT,
  batch TEXT,
  stock INTEGER,
  min INTEGER,
  unit TEXT
);
CREATE TABLE IF NOT EXISTS rooms (
  pos INTEGER NOT NULL,
  id TEXT PRIMARY KEY,
  type TEXT,
  floor TEXT,
  beds INTEGER,
  occupied INTEGER,
  tariff INTEGER,
  occupant TEXT,
  status TEXT,
  patients TEXT
);
CREATE TABLE IF NOT EXISTS invoices (
  pos INTEGER NOT NULL,
  id TEXT PRIMARY KEY,
  patient TEXT,
  patientId TEXT,
  department TEXT,
  amount REAL,
  method TEXT,
  date TEXT,
  status TEXT,
  notes TEXT
);
CREATE TABLE IF NOT EXISTS diagnostics (
  pos INTEGER NOT NULL,
  id TEXT PRIMARY KEY,
  patient TEXT,
  patientId TEXT,
  test TEXT,
  slot TEXT,
  date TEXT,
  status TEXT
);
CREATE TABLE IF NOT EXISTS alerts (
  pos INTEGER NOT NULL,
  id TEXT PRIMARY KEY,
  "to" TEXT,
  template TEXT,
  time TEXT,
  date TEXT,
  status TEXT
);
"""


def db_path() -> Path:
    env = os.environ.get("DATABASE_PATH") or os.environ.get("MEDICORE_SQLITE")
    if env:
        return Path(env)
    return ROOT / "medicore-live.db"


def connect(use_db: bool = True):
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path), check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA foreign_keys=ON")
    return con


def qident(name: str) -> str:
    return '"' + name.replace('"', "") + '"'


def ensure_schema(con=None) -> None:
    own = con is None
    if own:
        con = connect()
    cur = con.cursor()
    cur.executescript(CREATE_SQL)
    con.commit()
    cur.close()
    if own:
        con.close()


def _to_cell(table: str, key: str, value):
    if (table, key) in JSON_FIELDS:
        return json.dumps(value if value is not None else [])
    if key in BOOL_FIELDS:
        return 1 if value else 0
    if key in INT_FIELDS:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0
    if key in FLOAT_FIELDS:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0
    if value is None:
        return ""
    return value


def _from_cell(table: str, key: str, value):
    if value is None:
        if key in BOOL_FIELDS:
            return False
        if key in INT_FIELDS:
            return 0
        if key in FLOAT_FIELDS:
            return 0
        if (table, key) in JSON_FIELDS:
            return []
        return ""
    if (table, key) in JSON_FIELDS:
        if isinstance(value, (bytes, bytearray)):
            value = value.decode("utf-8")
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return []
        return value
    if key in BOOL_FIELDS:
        return bool(value)
    if key in FLOAT_FIELDS:
        try:
            n = float(value)
            return int(n) if n.is_integer() else n
        except (TypeError, ValueError):
            return 0
    if key in INT_FIELDS:
        return int(value)
    return value


def load_store(name: str) -> list:
    if name not in STORE_FIELDS:
        return []
    fields = STORE_FIELDS[name]
    con = connect()
    cur = con.cursor()
    cols = ", ".join(qident(f) for f in fields)
    cur.execute(f"SELECT {cols} FROM {qident(name)} ORDER BY pos ASC, id ASC")
    rows = []
    for rec in cur.fetchall():
        item = {k: _from_cell(name, k, rec[k]) for k in fields}
        rows.append(item)
    cur.close()
    con.close()
    return rows


def save_store(name: str, payload) -> None:
    if name not in STORE_FIELDS:
        raise ValueError(f"Unknown store {name}")
    if not isinstance(payload, list):
        raise ValueError("Expected a list")
    fields = STORE_FIELDS[name]
    con = connect()
    cur = con.cursor()
    cur.execute(f"DELETE FROM {qident(name)}")
    if payload:
        cols = ["pos"] + fields
        placeholders = ", ".join(["?"] * len(cols))
        colsql = ", ".join(qident(c) for c in cols)
        sql = f"INSERT INTO {qident(name)} ({colsql}) VALUES ({placeholders})"
        batch = []
        for i, row in enumerate(payload):
            vals = [i]
            for k in fields:
                vals.append(_to_cell(name, k, (row or {}).get(k)))
            batch.append(tuple(vals))
        cur.executemany(sql, batch)
    con.commit()
    cur.close()
    con.close()


def get_user(uid: str):
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT id, password_hash, role FROM users WHERE id=?", (uid,))
    row = cur.fetchone()
    cur.close()
    con.close()
    return dict(row) if row else None


def user_ids() -> set[str]:
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT id FROM users")
    ids = {r["id"] for r in cur.fetchall()}
    cur.close()
    con.close()
    return ids


def list_user_ids() -> list[str]:
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT id FROM users ORDER BY id")
    ids = [r["id"] for r in cur.fetchall()]
    cur.close()
    con.close()
    return ids


def upsert_user(uid: str, password_hash: str, role: str, replace_hash: bool = False) -> None:
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT id FROM users WHERE id=?", (uid,))
    if cur.fetchone():
        if replace_hash:
            cur.execute(
                "UPDATE users SET role=?, password_hash=? WHERE id=?",
                (role, password_hash, uid),
            )
        else:
            cur.execute("UPDATE users SET role=? WHERE id=?", (role, uid))
    else:
        cur.execute(
            "INSERT INTO users (id, password_hash, role) VALUES (?, ?, ?)",
            (uid, password_hash, role),
        )
    con.commit()
    cur.close()
    con.close()


def count_role(role: str) -> int:
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) AS n FROM users WHERE role=?", (role,))
    n = cur.fetchone()["n"]
    cur.close()
    con.close()
    return n


def users_empty() -> bool:
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT 1 FROM users LIMIT 1")
    empty = cur.fetchone() is None
    cur.close()
    con.close()
    return empty


def store_empty(name: str) -> bool:
    con = connect()
    cur = con.cursor()
    cur.execute(f"SELECT 1 FROM {qident(name)} LIMIT 1")
    empty = cur.fetchone() is None
    cur.close()
    con.close()
    return empty


def delete_user(uid: str, role: str | None = None) -> None:
    con = connect()
    cur = con.cursor()
    if role:
        cur.execute("DELETE FROM users WHERE id=? AND role=?", (uid, role))
    else:
        cur.execute("DELETE FROM users WHERE id=?", (uid,))
    con.commit()
    cur.close()
    con.close()


def set_role_patterns() -> None:
    con = connect()
    cur = con.cursor()
    cur.execute("UPDATE users SET role='staff' WHERE id LIKE 'DOC-%' AND (role IS NULL OR role='')")
    cur.execute(
        "UPDATE users SET role='patient' WHERE id LIKE 'P-%' AND (role IS NULL OR role='' OR role='staff')"
    )
    con.commit()
    cur.close()
    con.close()
