#!/usr/bin/env python3
"""MediCore login IDs — staff, patient, admin. Rebuild after seed changes."""
from __future__ import annotations

import json
import os
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from logins import (  # noqa: E402
    ADMIN_ID,
    ADMIN_PASSWORD,
    SEED_STAFF,
    STAFF_PASSWORD,
    patient_password,
)

OUT = os.path.join(ROOT, "MediCore-Login-IDs.pdf")

TEAL = colors.HexColor("#0F766E")
DEEP = colors.HexColor("#123C38")
CREAM = colors.HexColor("#F5F2EC")
LINE = colors.HexColor("#E4DDD2")
TEXT = colors.HexColor("#134E4A")
MUTED = colors.HexColor("#5C6B68")
WHITE = colors.white
ROSE = colors.HexColor("#9F1239")


def styles():
    b = getSampleStyleSheet()
    return {
        "kicker": ParagraphStyle("kicker", parent=b["Normal"], fontName="Helvetica-Bold",
                                 fontSize=9, textColor=TEAL, spaceAfter=6, leading=12),
        "cover": ParagraphStyle("cover", parent=b["Title"], fontName="Helvetica-Bold",
                                fontSize=26, textColor=DEEP, leading=32, alignment=TA_LEFT, spaceAfter=10),
        "lead": ParagraphStyle("lead", parent=b["Normal"], fontName="Helvetica",
                               fontSize=11, textColor=MUTED, leading=16, spaceAfter=8),
        "h1": ParagraphStyle("h1", parent=b["Heading1"], fontName="Helvetica-Bold",
                             fontSize=14, textColor=DEEP, spaceBefore=8, spaceAfter=6, leading=18),
        "body": ParagraphStyle("body", parent=b["BodyText"], fontName="Helvetica",
                               fontSize=9.5, textColor=TEXT, leading=13.5, spaceAfter=5),
        "th": ParagraphStyle("th", parent=b["Normal"], fontName="Helvetica-Bold",
                             fontSize=8, textColor=WHITE, leading=11),
        "td": ParagraphStyle("td", parent=b["Normal"], fontName="Helvetica",
                             fontSize=8.5, textColor=TEXT, leading=12),
        "tdc": ParagraphStyle("tdc", parent=b["Normal"], fontName="Helvetica-Bold",
                              fontSize=8.5, textColor=DEEP, leading=12),
        "warn": ParagraphStyle("warn", parent=b["Normal"], fontName="Helvetica",
                               fontSize=9, textColor=ROSE, leading=13, spaceAfter=8),
        "code": ParagraphStyle("code", parent=b["Normal"], fontName="Courier-Bold",
                               fontSize=10, textColor=DEEP, leading=14, spaceAfter=2),
    }


def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(DEEP)
    canvas.rect(0, h - 13 * mm, w, 13 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(16 * mm, h - 8 * mm, "MediCore Hospital  ·  Login IDs")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w - 16 * mm, h - 8 * mm, "Internal / demo use only")
    canvas.setFillColor(TEAL)
    canvas.rect(0, 0, w, 11 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(16 * mm, 4.5 * mm, "Do not publish this PDF on the website.")
    canvas.drawRightString(w - 16 * mm, 4.5 * mm, "Page %d" % doc.page)
    canvas.restoreState()


def table(rows, widths):
    t = Table(rows, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, CREAM]),
    ]))
    return t


def load_patients():
    try:
        from mysql_db import load_store
        return load_store("patients")
    except Exception:
        backup = os.path.join(ROOT, "BACKUP", "medicore-data.json")
        if os.path.isfile(backup):
            data = json.loads(open(backup, encoding="utf-8").read())
            return (data.get("stores") or {}).get("patients") or []
        return []


def build():
    st = styles()
    P = lambda t, k="body": Paragraph(str(t), st[k])
    story = []
    story.append(P("CREDENTIALS SHEET", "kicker"))
    story.append(P("How to sign in to MediCore Hospital", "cover"))
    story.append(P(
        "Three doors: Staff run the wards, a Patient sees only their own file, "
        "Admin can switch Staff / Patients / Combined at the top right."
    , "lead"))
    story.append(P(
        "Start the site: open Desktop → MediCore-Pages → SERVER and double-click "
        "<b>START SERVER AND DATABASE.command</b>. Then open http://127.0.0.1:5000 "
        "and choose Sign in.",
        "body",
    ))
    story.append(P(
        "Passwords are stored as hashes in MySQL. This sheet lists the demo passwords so you can teach the system.",
        "warn",
    ))

    story.append(P("1. Three login types", "h1"))
    head = [P(x, "th") for x in ("Tab", "ID example", "Password", "Opens")]
    rows = [head]
    for line in (
        ("Staff", "DOC-1001", STAFF_PASSWORD, "Hospital dashboard"),
        ("Patient", "P-4821", "Aarav21", "That patient’s file only"),
        ("Admin", ADMIN_ID, ADMIN_PASSWORD, "Full access + view switch"),
    ):
        rows.append([P(line[0], "tdc"), P(line[1], "td"), P(line[2], "tdc"), P(line[3], "td")])
    story.append(table(rows, [28 * mm, 38 * mm, 36 * mm, 76 * mm]))
    story.append(Spacer(1, 8))

    story.append(P("2. Administrator", "h1"))
    story.append(P(f"ID &nbsp;&nbsp;<b>{ADMIN_ID}</b>", "code"))
    story.append(P(f"Password &nbsp;&nbsp;<b>{ADMIN_PASSWORD}</b>", "code"))
    story.append(P(
        "After sign-in, use the three pills at the top right: <b>Staff</b> (wards, pharmacy, billing), "
        "<b>Patients</b> (every portal file), <b>Combined</b> (both).",
        "body",
    ))

    story.append(P("3. Staff (doctors)", "h1"))
    story.append(P(f"Shared password for every staff ID: <b>{STAFF_PASSWORD}</b>", "body"))
    head = [P(x, "th") for x in ("Staff ID", "Password", "Notes")]
    srows = [head]
    for sid in SEED_STAFF:
        srows.append([P(sid, "tdc"), P(STAFF_PASSWORD, "td"), P("Doctor console", "td")])
    story.append(table(srows, [50 * mm, 40 * mm, 88 * mm]))
    story.append(Spacer(1, 8))

    story.append(P("4. Patients (portal)", "h1"))
    story.append(P(
        "ID is <b>P-</b> plus four digits. Password is the <b>first name</b> (letters only) plus the "
        "<b>last two digits</b> of the ID. Example: Aarav Sharma + P-4821 → <b>Aarav21</b>.",
        "body",
    ))
    story.append(P(
        "A patient sees only their details, reports, appointments and bills, and can pay an open bill. "
        "They cannot open another patient’s file.",
        "body",
    ))
    patients = load_patients()
    head = [P(x, "th") for x in ("Patient ID", "Name", "Password", "What they see")]
    prows = [head]
    if not patients:
        prows.append([P("Start the server once so MySQL has patient rows.", "td"), P("", "td"), P("", "td"), P("", "td")])
    for p in patients:
        pid = p.get("id") or ""
        name = p.get("name") or ""
        pw = patient_password(name, pid)
        prows.append([
            P(pid, "tdc"),
            P(name, "td"),
            P(pw, "tdc"),
            P("Own reports, bills, details", "td"),
        ])
    story.append(table(prows, [32 * mm, 48 * mm, 36 * mm, 62 * mm]))
    story.append(Spacer(1, 8))

    story.append(P("5. New patients", "h1"))
    story.append(P(
        "When staff click Register patient, the server creates a new P-xxxx ID and a portal password "
        "(first name + last two digits). That password is shown once on screen — copy it for the patient. "
        "Rebuild this PDF after you add people if you want the sheet to stay complete.",
        "body",
    ))

    doc = SimpleDocTemplate(
        OUT, pagesize=A4,
        leftMargin=16 * mm, rightMargin=16 * mm,
        topMargin=20 * mm, bottomMargin=16 * mm,
        title="MediCore login IDs",
        author="MediCore Hospital",
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print("Wrote", OUT)


if __name__ == "__main__":
    build()
