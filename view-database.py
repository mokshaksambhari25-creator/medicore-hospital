#!/usr/bin/env python3
"""
Show everything in the MediCore MySQL database (no password hashes).
Run anytime — the website server does not need to be on.

  cd ~/Desktop/MediCore-Pages
  python3 view-database.py
"""
import json
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from mysql_cfg import STORE_FIELDS, load_mysql_cfg
from mysql_db import list_user_ids, load_store

OUT = ROOT / "database-view.html"


def load():
    users = [{"id": uid} for uid in list_user_ids()]
    stores = {name: load_store(name) for name in STORE_FIELDS}
    return users, stores


def line(title, n):
    print()
    print("=" * 60)
    print(f"  {title}  ({n})")
    print("=" * 60)


def main():
    cfg = load_mysql_cfg()
    users, stores = load()
    where = f"{cfg['user']}@{cfg['host']}:{cfg['port']}/{cfg['database']}"
    print("MediCore database  (MySQL)")
    print("Connect:", where)

    line("Logins (users table)", len(users))
    print("  Password is stored as a hash — not shown here.")
    for u in users:
        print("  •", u["id"])

    order = list(STORE_FIELDS.keys())
    preferred = ["doctors", "patients", "rooms", "appointments", "invoices", "pharmacy", "diagnostics", "alerts"]
    order = [n for n in preferred if n in stores] + [n for n in order if n not in preferred]

    for name in order:
        rows = stores.get(name, [])
        line(name, len(rows))
        if not rows:
            print("  (empty)")
            continue
        keys = list(rows[0].keys())
        show = [k for k in keys if k != "patients"][:6]
        for row in rows:
            bits = []
            for k in show:
                v = row.get(k)
                if isinstance(v, bool):
                    v = "yes" if v else "no"
                bits.append(f"{k}={v}")
            extra = row.get("patients")
            if extra:
                bits.append("patients=" + ", ".join(extra))
            print("  • " + " | ".join(bits))

    html_parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        "<title>MediCore database view</title>",
        "<style>body{font-family:Inter,system-ui,sans-serif;background:#F5F2EC;color:#134E4A;",
        "max-width:960px;margin:24px auto;padding:0 16px;line-height:1.45}",
        "h1{color:#0B2E2B} h2{color:#0F766E;margin-top:28px}",
        "table{border-collapse:collapse;width:100%;background:#fff;font-size:13px}",
        "th{background:#123C38;color:#fff;text-align:left;padding:8px}",
        "td{border-bottom:1px solid #E4DDD2;padding:7px 8px;vertical-align:top}",
        "tr:nth-child(even){background:#FAF8F4}",
        ".meta{color:#5C6B68;font-size:13px} code{font-size:13px}</style></head><body>",
        "<h1>MediCore database (MySQL)</h1>",
        f"<p class='meta'>Connect: <code>{where}</code></p>",
        "<p class='meta'>Password for local MySQL user <code>medicore</code>: <code>MediCore24</code>. "
        "A downloadable dump is in <code>BACKUP/medicore.sql</code>.</p>",
        "<p class='meta'>This is a snapshot. Run <code>python3 view-database.py</code> again after you save in the site.</p>",
        f"<h2>Logins ({len(users)})</h2>",
        "<p>IDs that can sign in. Passwords are hashed in the database and are not listed.</p><ul>",
    ]
    for u in users:
        html_parts.append(f"<li><b>{u['id']}</b></li>")
    html_parts.append("</ul>")

    for name in order:
        rows = stores.get(name, [])
        html_parts.append(f"<h2>{name} ({len(rows)})</h2>")
        if not rows:
            html_parts.append("<p>(empty)</p>")
            continue
        keys = list(rows[0].keys())
        html_parts.append("<table><tr>" + "".join(f"<th>{k}</th>" for k in keys) + "</tr>")
        for row in rows:
            tds = []
            for k in keys:
                v = row.get(k)
                if isinstance(v, list):
                    v = ", ".join(str(x) for x in v)
                elif isinstance(v, bool):
                    v = "yes" if v else "no"
                tds.append(f"<td>{v}</td>")
            html_parts.append("<tr>" + "".join(tds) + "</tr>")
        html_parts.append("</table>")
    html_parts.append("</body></html>")
    OUT.write_text("".join(html_parts), encoding="utf-8")
    print()
    print("Also wrote a table view you can open in the browser:")
    print(" ", OUT)
    if "--no-browser" not in sys.argv:
        webbrowser.open(OUT.as_uri())


if __name__ == "__main__":
    main()
