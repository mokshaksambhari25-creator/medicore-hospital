"""Pick MySQL when it is reachable, otherwise SQLite so the site always starts."""
from __future__ import annotations

import os

_BACKEND = None
_KIND = "sqlite"


def kind() -> str:
    _pick()
    return _KIND


def _pick():
    global _BACKEND, _KIND
    if _BACKEND is not None:
        return _BACKEND
    forced = (os.environ.get("MEDICORE_DB") or "").strip().lower()
    if not forced and os.environ.get("RENDER"):
        forced = "sqlite"
    if forced == "sqlite":
        import sqlite_db as backend

        _KIND = "sqlite"
        _BACKEND = backend
        return backend
    if forced != "mysql":
        try:
            import mysql_db as backend

            con = backend.connect()
            con.close()
            _KIND = "mysql"
            _BACKEND = backend
            return backend
        except Exception:
            pass
    elif forced == "mysql":
        import mysql_db as backend

        _KIND = "mysql"
        _BACKEND = backend
        return backend
    import sqlite_db as backend

    _KIND = "sqlite"
    _BACKEND = backend
    return backend


def __getattr__(name):
    return getattr(_pick(), name)
