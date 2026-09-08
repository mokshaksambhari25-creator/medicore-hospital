#!/usr/bin/env python3
"""Copy the SQLite backup into local MySQL. Safe to re-run (replaces MySQL rows)."""
from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mysql_cfg import STORE_FIELDS, load_mysql_cfg  # noqa: E402
from mysql_db import ensure_schema, save_store, connect, list_user_ids  # noqa: E402

SQLITE = ROOT / "BACKUP" / "medicore-sqlite.db"
if not SQLITE.is_file():
    SQLITE = ROOT / "medicore.db"
JSON_BACKUP = ROOT / "BACKUP" / "medicore-data.json"
SQL_DUMP = ROOT / "BACKUP" / "medicore.sql"


def load_sqlite():
    if JSON_BACKUP.is_file() and not SQLITE.is_file():
        data = json.loads(JSON_BACKUP.read_text(encoding="utf-8"))
        return data.get("users_full") or [], data.get("stores") or {}
    con = sqlite3.connect(SQLITE)
    con.row_factory = sqlite3.Row
    users = [dict(r) for r in con.execute("SELECT id, password_hash, role FROM users")]
    stores = {}
    for name, payload in con.execute("SELECT name, payload FROM stores"):
        stores[name] = json.loads(payload)
    con.close()
    return users, stores


def dump_sql():
    cfg = load_mysql_cfg()
    env = os.environ.copy()
    env["MYSQL_PWD"] = cfg["password"]
    cmd = [
        "mysqldump",
        "-h", cfg["host"],
        "-P", str(cfg["port"]),
        "-u", cfg["user"],
        "--databases", cfg["database"],
        "--skip-comments",
        "--default-character-set=utf8mb4",
    ]
    try:
        out = subprocess.check_output(cmd, env=env, stderr=subprocess.STDOUT)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print("Could not write .sql dump yet:", exc)
        return
    SQL_DUMP.write_bytes(out)
    print("SQL dump:", SQL_DUMP)


def main():
    users, stores = load_sqlite()
    print("Source:", SQLITE if SQLITE.is_file() else JSON_BACKUP)
    print("SQLite users:", len(users))
    for name, rows in stores.items():
        print(f"  {name}: {len(rows)}")

    ensure_schema()
    con = connect()
    cur = con.cursor()
    cur.execute("DELETE FROM users")
    for u in users:
        cur.execute(
            "INSERT INTO users (id, password_hash, role) VALUES (%s, %s, %s)",
            (u["id"], u["password_hash"], u.get("role") or "staff"),
        )
    cur.close()
    con.close()

    for name in STORE_FIELDS:
        save_store(name, stores.get(name) or [])

    print()
    print("MySQL users:", len(list_user_ids()))
    con = connect()
    cur = con.cursor()
    for name in STORE_FIELDS:
        cur.execute(f"SELECT COUNT(*) AS n FROM `{name}`")
        n = cur.fetchone()["n"]
        src = len(stores.get(name) or [])
        mark = "OK" if n == src else "MISMATCH"
        print(f"  {name}: {n}  (sqlite {src})  {mark}")
        if n != src:
            raise SystemExit("Count mismatch — aborting before the site switches.")
    cur.close()
    con.close()
    dump_sql()
    print("Migration complete.")


if __name__ == "__main__":
    main()
