#!/usr/bin/env python3
"""
MediCore launcher — start the website, open the MySQL database, or both.

Used by the double-click files in this folder, or from Terminal:

    python3 control.py start-all
    python3 control.py start
    python3 control.py database
    python3 control.py stop
    python3 control.py gui
"""
from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
APP = ROOT / "app.py"
VIEW_DB = ROOT / "view-database.py"
DB_HTML = ROOT / "database-view.html"
ENSURE_MYSQL = HERE / "ensure_mysql.sh"
SQL_DUMP = ROOT / "BACKUP" / "medicore.sql"
PID_FILE = HERE / "medicore.pid"
LOG_FILE = HERE / "medicore.log"
URL = "http://127.0.0.1:5000"
PORT = 5000
BRAVE_APPS = (
    "/Applications/Brave Browser.app",
    str(Path.home() / "Applications/Brave Browser.app"),
)


def python_bin() -> str:
    return sys.executable or "python3"


def port_open() -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.4)
    try:
        sock.connect(("127.0.0.1", PORT))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def pid_from_file() -> int | None:
    if not PID_FILE.is_file():
        return None
    try:
        pid = int(PID_FILE.read_text().strip())
    except ValueError:
        return None
    try:
        os.kill(pid, 0)
        return pid
    except OSError:
        return None


def server_pid() -> int | None:
    pid = pid_from_file()
    if pid:
        return pid
    try:
        out = subprocess.check_output(
            ["lsof", "-nP", f"-iTCP:{PORT}", "-sTCP:LISTEN", "-t"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    for line in out.split():
        if line.isdigit():
            return int(line)
    return None


def is_running() -> bool:
    return port_open()


def ensure_flask() -> None:
    try:
        import flask  # noqa: F401
        from werkzeug.security import check_password_hash  # noqa: F401
    except ImportError:
        print("Installing Flask (needed once)…")
        subprocess.check_call(
            [python_bin(), "-m", "pip", "install", "--user", "flask", "werkzeug"]
        )
    try:
        import pymysql  # noqa: F401
    except ImportError:
        print("Installing PyMySQL (needed once)…")
        subprocess.check_call([python_bin(), "-m", "pip", "install", "--user", "pymysql"])


def ensure_mysql() -> str:
    if not ENSURE_MYSQL.is_file():
        return "Missing SERVER/ensure_mysql.sh"
    try:
        subprocess.check_call(["/bin/zsh", str(ENSURE_MYSQL)], cwd=str(HERE))
        return "MySQL is ready."
    except subprocess.CalledProcessError as exc:
        return f"Could not start MySQL ({exc.returncode}). Try: brew services start mysql"


def open_brave(target: str) -> None:
    for app in BRAVE_APPS:
        if Path(app).exists():
            subprocess.run(["open", "-a", app, target], check=False)
            return
    subprocess.run(["open", target], check=False)


def wait_until_up(seconds: float = 20) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if port_open():
            return True
        time.sleep(0.25)
    return False


def start_server(open_browser: bool = True) -> str:
    if not APP.is_file():
        return f"Cannot find app.py at {APP}"
    ensure_flask()
    mysql_msg = ensure_mysql()
    if mysql_msg.startswith("Could not"):
        return mysql_msg
    if is_running():
        if open_browser:
            open_brave(URL)
        return f"Server already running at {URL}"

    LOG_FILE.write_text("")
    proc = subprocess.Popen(
        [python_bin(), str(APP)],
        cwd=str(ROOT),
        stdout=open(LOG_FILE, "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    PID_FILE.write_text(str(proc.pid))
    if not wait_until_up():
        tail = LOG_FILE.read_text()[-800:] if LOG_FILE.is_file() else ""
        return "Server did not start.\n" + (tail or "Check that port 5000 is free.")
    if open_browser:
        open_brave(URL)
    return f"Server started at {URL}"


def stop_server() -> str:
    pid = server_pid()
    if not pid and not is_running():
        if PID_FILE.exists():
            PID_FILE.unlink()
        return "Server is not running."
    if pid:
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError, OSError):
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass
    for _ in range(20):
        if not is_running():
            break
        time.sleep(0.15)
    if is_running() and pid:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    if PID_FILE.exists():
        PID_FILE.unlink()
    return "Server stopped."


def open_database() -> str:
    ensure_flask()
    mysql_msg = ensure_mysql()
    if mysql_msg.startswith("Could not"):
        return mysql_msg
    if not VIEW_DB.is_file():
        return f"Cannot find view-database.py at {VIEW_DB}"
    subprocess.check_call(
        [python_bin(), str(VIEW_DB), "--no-browser"],
        cwd=str(ROOT),
    )
    if not DB_HTML.is_file():
        return "Database view was not created."
    open_brave(DB_HTML.as_uri())
    extra = ""
    if SQL_DUMP.is_file():
        extra = f"\nSQL dump (copy this file): {SQL_DUMP}"
    return (
        "MySQL opened in Brave.\n"
        "Host 127.0.0.1  ·  database medicore  ·  user medicore  ·  password MediCore24"
        + extra
    )


def start_all() -> str:
    msg = start_server(open_browser=True)
    db_msg = open_database()
    return msg + "\n" + db_msg


def status_text() -> str:
    if is_running():
        return f"Server ON  ·  {URL}"
    return "Server OFF"


def print_banner(title: str) -> None:
    print()
    print("=" * 52)
    print(f"  MediCore  ·  {title}")
    print("=" * 52)
    print()


def run_gui() -> None:
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.title("MediCore")
    root.configure(bg="#0B2E2B")
    root.resizable(False, False)
    root.geometry("420x520")

    def run(action, title):
        try:
            result = action()
        except Exception as exc:
            result = str(exc)
        status_var.set(status_text())
        note_var.set(result)
        messagebox.showinfo(title, result)

    pad = {"padx": 28, "pady": 6}

    tk.Label(
        root,
        text="MediCore",
        fg="#F5F2EC",
        bg="#0B2E2B",
        font=("Inter", 26, "bold"),
    ).pack(pady=(28, 0))
    tk.Label(
        root,
        text="Hospital suite launcher",
        fg="#A7C4C0",
        bg="#0B2E2B",
        font=("Inter", 12),
    ).pack(pady=(0, 18))

    status_var = tk.StringVar(value=status_text())
    tk.Label(
        root,
        textvariable=status_var,
        fg="#5EEAD4",
        bg="#123C38",
        font=("Inter", 12, "bold"),
        pady=10,
    ).pack(fill="x", padx=28, pady=(0, 16))

    def btn(label, command, fill="#0F766E"):
        b = tk.Button(
            root,
            text=label,
            command=command,
            bg=fill,
            fg="#F5F2EC",
            activebackground="#14B8A6",
            activeforeground="#0B2E2B",
            relief="flat",
            font=("Inter", 13, "bold"),
            cursor="hand2",
            pady=11,
        )
        b.pack(fill="x", **pad)
        return b

    btn(
        "Start server + database",
        lambda: run(start_all, "Server + database"),
        "#0F766E",
    )
    btn("Start server only", lambda: run(lambda: start_server(True), "Server"))
    btn("Open database", lambda: run(open_database, "Database"))
    btn("Stop server", lambda: run(stop_server, "Stop"), "#7F1D1D")

    note_var = tk.StringVar(
        value="Double-click a button.\nWebsite:  http://127.0.0.1:5000\nStaff ID example: DOC-1001   Password: 123456"
    )
    tk.Label(
        root,
        textvariable=note_var,
        fg="#C5D5D2",
        bg="#0B2E2B",
        font=("Inter", 11),
        justify="left",
        wraplength=360,
    ).pack(fill="x", padx=28, pady=(18, 12))

    root.mainloop()


def usage() -> None:
    print("Usage: python3 control.py [gui|start-all|start|database|stop|status]")


def main(argv: list[str]) -> int:
    cmd = (argv[1] if len(argv) > 1 else "gui").lower()
    if cmd in ("gui", "panel", "menu"):
        run_gui()
        return 0
    if cmd in ("start-all", "all", "both"):
        print_banner("Start server + database")
        print(start_all())
        print()
        print("Leave this window, or close it — the server keeps running.")
        print("Stop it later with  STOP SERVER.command")
        return 0
    if cmd in ("start", "server"):
        print_banner("Start server")
        print(start_server(True))
        return 0
    if cmd in ("database", "db", "open-db"):
        print_banner("Open database")
        print(open_database())
        return 0
    if cmd in ("stop", "quit"):
        print_banner("Stop server")
        print(stop_server())
        return 0
    if cmd == "status":
        print(status_text())
        return 0
    usage()
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
