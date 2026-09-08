"""Shared MediCore login IDs — used by the server and the credentials PDF."""
from __future__ import annotations

ADMIN_ID = "ADMIN-1000"
ADMIN_PASSWORD = "Admin24"
ADMIN_NAME = "Hospital Admin"
STAFF_PASSWORD = "123456"

# Seed patients: portal ID is P- plus four digits. Password = first name + last two digits.
SEED_PORTAL = (
    ("P-4821", "Aarav Sharma"),
    ("P-3304", "Ritu Verma"),
    ("P-7718", "Nikhil Patil"),
    ("P-2196", "Sneha Patil"),
    ("P-6402", "Fatima Khan"),
    ("P-5580", "Kabir Reddy"),
)

SEED_STAFF = tuple(f"DOC-100{i}" for i in range(1, 7))


def patient_password(name: str, pid: str) -> str:
    first = "".join(ch for ch in (name or "").split()[0] if ch.isalpha()) or "Patient"
    digits = "".join(ch for ch in (pid or "") if ch.isdigit())[-2:].zfill(2)
    return first + digits


def name_to_seed_id() -> dict[str, str]:
    return {name: pid for pid, name in SEED_PORTAL}
