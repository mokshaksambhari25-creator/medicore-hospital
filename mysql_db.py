"""MySQL storage for MediCore — real tables, same list API as the old SQLite stores."""
from __future__ import annotations

import json
from decimal import Decimal

import pymysql
from pymysql.cursors import DictCursor

from mysql_cfg import (
    BOOL_FIELDS,
    CREATE_SQL,
    FLOAT_FIELDS,
    INT_FIELDS,
    JSON_FIELDS,
    STORE_FIELDS,
    load_mysql_cfg,
)

STORES = tuple(STORE_FIELDS.keys())


def connect(use_db: bool = True):
    cfg = load_mysql_cfg()
    kw = {
        "host": cfg["host"],
        "port": cfg["port"],
        "user": cfg["user"],
        "password": cfg["password"],
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
        "autocommit": True,
        "connect_timeout": 3,
    }
    if use_db:
        kw["database"] = cfg["database"]
    return pymysql.connect(**kw)


def qident(name: str) -> str:
    return "`" + name.replace("`", "") + "`"


def ensure_schema(con=None) -> None:
    own = con is None
    if own:
        con = connect()
    cur = con.cursor()
    for stmt in CREATE_SQL.split(";"):
        sql = stmt.strip()
        if sql:
            cur.execute(sql)
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
        if isinstance(value, Decimal):
            n = float(value)
            return int(n) if n.is_integer() else n
        return value
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
        item = {k: _from_cell(name, k, rec.get(k)) for k in fields}
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
        placeholders = ", ".join(["%s"] * len(cols))
        colsql = ", ".join(qident(c) for c in cols)
        sql = f"INSERT INTO {qident(name)} ({colsql}) VALUES ({placeholders})"
        batch = []
        for i, row in enumerate(payload):
            vals = [i]
            for k in fields:
                vals.append(_to_cell(name, k, (row or {}).get(k)))
            batch.append(tuple(vals))
        cur.executemany(sql, batch)
    cur.close()
    con.close()


def get_user(uid: str):
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT id, password_hash, role FROM users WHERE id=%s", (uid,))
    row = cur.fetchone()
    cur.close()
    con.close()
    return row


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
    cur.execute("SELECT id FROM users WHERE id=%s", (uid,))
    if cur.fetchone():
        if replace_hash:
            cur.execute(
                "UPDATE users SET role=%s, password_hash=%s WHERE id=%s",
                (role, password_hash, uid),
            )
        else:
            cur.execute("UPDATE users SET role=%s WHERE id=%s", (role, uid))
    else:
        cur.execute(
            "INSERT INTO users (id, password_hash, role) VALUES (%s, %s, %s)",
            (uid, password_hash, role),
        )
    cur.close()
    con.close()


def count_role(role: str) -> int:
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) AS n FROM users WHERE role=%s", (role,))
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
        cur.execute("DELETE FROM users WHERE id=%s AND role=%s", (uid, role))
    else:
        cur.execute("DELETE FROM users WHERE id=%s", (uid,))
    cur.close()
    con.close()


def set_role_patterns() -> None:
    con = connect()
    cur = con.cursor()
    cur.execute("UPDATE users SET role='staff' WHERE id LIKE 'DOC-%' AND (role IS NULL OR role='')")
    cur.execute(
        "UPDATE users SET role='patient' WHERE id LIKE 'P-%' AND (role IS NULL OR role='' OR role='staff')"
    )
    cur.close()
    con.close()
