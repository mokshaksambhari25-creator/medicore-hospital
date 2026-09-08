#!/usr/bin/env python3
"""Build MediCore-How-It-Works.pdf — English + Hinglish, diagrams, full walkthrough."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image as RLImage,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "MediCore-How-It-Works.pdf"
IMG = ROOT / "_diagrams"
TEAL = colors.HexColor("#0F766E")
INK = colors.HexColor("#0B2E2B")
MUTED = colors.HexColor("#5C6B68")
CREAM = colors.HexColor("#F5F2EC")
SIDE = colors.HexColor("#123C38")
LINE = colors.HexColor("#E4DDD2")
WHITE = colors.white


def font(size, bold=False):
    path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def rounded(draw, xy, r, fill, outline=None, width=2):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def centre(draw, xy, text, fnt, fill=(255, 255, 255)):
    x0, y0, x1, y1 = xy
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((x0 + x1 - tw) / 2, (y0 + y1 - th) / 2 - 2), text, font=fnt, fill=fill)


def draw_pages_map() -> Path:
    IMG.mkdir(exist_ok=True)
    w, h = 1600, 1100
    im = Image.new("RGB", (w, h), (245, 242, 236))
    d = ImageDraw.Draw(im)
    title, body, small = font(28, True), font(18, True), font(16)
    d.text((48, 28), "Mindmap 1 — All pages of MediCore", font=title, fill=(11, 46, 43))
    d.text((48, 70), "Public site  ·  Staff / Admin console  ·  Patient portal", font=small, fill=(92, 107, 104))
    # hub
    hub = (620, 140, 980, 230)
    rounded(d, hub, 18, (15, 118, 110))
    centre(d, hub, "MediCore Hospital website", body, (255, 255, 255))
    groups = [
        (40, 300, 500, 1040, "PUBLIC (no login)", (18, 60, 56), [
            "Home — hospital intro",
            "About — our story",
            "Departments — 8 specialties",
            "Facilities — beds, ICU, canteen",
            "Book — slot without login",
            "Contact — address & emergency",
            "Sign in — Staff / Patient / Admin",
        ]),
        (550, 300, 1050, 1040, "AFTER LOGIN — STAFF / ADMIN", (15, 118, 110), [
            "Dashboard — live numbers",
            "Patients — register / edit",
            "Doctors — roster",
            "Appointments — queue",
            "Pharmacy — stock",
            "Ward Allotment — beds",
            "Diagnostics — scans",
            "Payments — bills",
            "Reports — print summary",
            "Email & SMS — message log",
            "Admin switch: Staff / Patients / Admin",
        ]),
        (1100, 300, 1560, 700, "PATIENT PORTAL", (180, 83, 9), [
            "My details (own file only)",
            "Reports",
            "Bills + Pay (UPI / card)",
            "Appointments",
            "Hindi / English toggle",
        ]),
    ]
    for x0, y0, x1, y1, head, col, items in groups:
        rounded(d, (x0, y0, x1, y1), 20, (255, 255, 255), col, 3)
        rounded(d, (x0, y0, x1, y0 + 48), 0, col)
        d.text((x0 + 16, y0 + 12), head, font=body, fill=(255, 255, 255))
        yy = y0 + 64
        for it in items:
            d.ellipse((x0 + 18, yy + 6, x0 + 28, yy + 16), fill=col)
            d.text((x0 + 38, yy), it, font=small, fill=(11, 46, 43))
            yy += 32
        # line from hub
        d.line((800, 230, (x0 + x1) / 2, y0), fill=col, width=3)
    path = IMG / "map-pages.png"
    im.save(path, "PNG")
    return path


def draw_flow_map() -> Path:
    IMG.mkdir(exist_ok=True)
    w, h = 1600, 900
    im = Image.new("RGB", (w, h), (245, 242, 236))
    d = ImageDraw.Draw(im)
    title, body, small = font(28, True), font(18, True), font(16)
    d.text((48, 24), "Mindmap 2 — How a click becomes data", font=title, fill=(11, 46, 43))
    d.text((48, 66), "Browser  →  Server (Flask)  →  Database  →  Screen updates", font=small, fill=(92, 107, 104))
    boxes = [
        (60, 160, 360, 320, (18, 60, 56), "1. You click", "Open a page or press\nSave / Sign in / Book"),
        (420, 160, 720, 320, (15, 118, 110), "2. Server", "Flask on this Mac or\nRender (gunicorn)"),
        (780, 160, 1080, 320, (29, 78, 216), "3. Database", "MySQL (Mac) or\nSQLite (live site)"),
        (1140, 160, 1540, 320, (4, 120, 87), "4. Answer", "HTML page or JSON\nlist of patients, bills…"),
        (60, 420, 760, 820, (18, 60, 56), "Public click", "Home / Book / Contact\nServer sends the HTML file.\nBook also writes a Pending\nappointment in the database."),
        (840, 420, 1540, 820, (15, 118, 110), "After login", "Sign in checks the users table.\nEach Save sends PUT /api/store/…\nDatabase replaces that list.\nNext Dashboard load shows new data."),
    ]
    for x0, y0, x1, y1, col, head, txt in boxes:
        rounded(d, (x0, y0, x1, y1), 18, (255, 255, 255), col, 3)
        rounded(d, (x0, y0, x1, y0 + 52), 0, col)
        d.text((x0 + 16, y0 + 14), head, font=body, fill=(255, 255, 255))
        yy = y0 + 70
        for line in txt.split("\n"):
            d.text((x0 + 18, yy), line, font=small, fill=(11, 46, 43))
            yy += 28
    for x in (360, 720, 1080):
        d.polygon([(x + 8, 230), (x + 48, 240), (x + 8, 250)], fill=(15, 118, 110))
    path = IMG / "map-flow.png"
    im.save(path, "PNG")
    return path


def draw_roles_map() -> Path:
    IMG.mkdir(exist_ok=True)
    w, h = 1600, 720
    im = Image.new("RGB", (w, h), (245, 242, 236))
    d = ImageDraw.Draw(im)
    title, body, small = font(28, True), font(18, True), font(16)
    d.text((48, 24), "Who can open what", font=title, fill=(11, 46, 43))
    roles = [
        (50, 100, 520, 680, (15, 118, 110), "STAFF", "Doctor / nurse desk", [
            "Full hospital console",
            "Add / edit patients",
            "Book and confirm slots",
            "Pharmacy, wards, bills",
            "Cannot see other staff passwords",
        ]),
        (540, 100, 1060, 680, (29, 78, 216), "PATIENT", "Own file only", [
            "Patient portal only",
            "Own reports and bills",
            "Pay own invoice",
            "Cannot open staff tabs",
            "Cannot see other patients",
        ]),
        (1080, 100, 1550, 680, (180, 83, 9), "ADMIN", "Whole hospital", [
            "Same as staff, plus",
            "Staff / Patients / Admin switch",
            "Patient portal list",
            "Sees staff floor and patients",
            "Used for hospital control",
        ]),
    ]
    for x0, y0, x1, y1, col, head, sub, items in roles:
        rounded(d, (x0, y0, x1, y1), 20, (255, 255, 255), col, 3)
        rounded(d, (x0, y0, x1, y0 + 88), 0, col)
        d.text((x0 + 20, y0 + 16), head, font=body, fill=(255, 255, 255))
        d.text((x0 + 20, y0 + 50), sub, font=small, fill=(227, 245, 243))
        yy = y0 + 110
        for it in items:
            d.ellipse((x0 + 22, yy + 6, x0 + 32, yy + 16), fill=col)
            d.text((x0 + 42, yy), it, font=small, fill=(11, 46, 43))
            yy += 36
    path = IMG / "map-roles.png"
    im.save(path, "PNG")
    return path


def styles():
    base = getSampleStyleSheet()
    s = {
        "cover": ParagraphStyle("cover", parent=base["Title"], fontName="Helvetica-Bold", fontSize=26, leading=32, textColor=WHITE, alignment=TA_CENTER, spaceAfter=8),
        "coversub": ParagraphStyle("coversub", parent=base["Normal"], fontName="Helvetica", fontSize=12, leading=16, textColor=colors.HexColor("#C5DDD9"), alignment=TA_CENTER),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=TEAL, spaceBefore=14, spaceAfter=8),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=INK, spaceBefore=10, spaceAfter=6),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontName="Helvetica", fontSize=10.5, leading=15, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6),
        "hi": ParagraphStyle("hi", parent=base["BodyText"], fontName="Helvetica-Oblique", fontSize=10.5, leading=15, textColor=INK, alignment=TA_LEFT, spaceAfter=2),
        "hiHead": ParagraphStyle("hiHead", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=TEAL, spaceAfter=4),
        "tiny": ParagraphStyle("tiny", parent=base["Normal"], fontName="Helvetica", fontSize=9, leading=12, textColor=MUTED),
        "center": ParagraphStyle("center", parent=base["Normal"], fontName="Helvetica", fontSize=10, leading=14, alignment=TA_CENTER, textColor=INK),
        "li": ParagraphStyle("li", parent=base["BodyText"], fontName="Helvetica", fontSize=10.5, leading=14.5, textColor=INK, leftIndent=4),
    }
    return s


def hinglish(s, title, text):
    head = Paragraph("Hinglish — kaise bolo", s["hiHead"])
    body = Paragraph(text, s["hi"])
    box = Table([[head], [body]], colWidths=[170 * mm])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CREAM),
        ("BOX", (0, 0), (-1, -1), 0.6, TEAL),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (0, 0), 8),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return KeepTogether([Spacer(1, 4), box, Spacer(1, 8)])


def bullets(s, items):
    return ListFlowable(
        [ListItem(Paragraph(i, s["li"]), leftIndent=12, bulletColor=TEAL) for i in items],
        bulletType="bullet",
        start="•",
        leftIndent=16,
        spaceAfter=8,
    )


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(SIDE)
    canvas.rect(0, A4[1] - 14 * mm, A4[0], 14 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(16 * mm, A4[1] - 9 * mm, "MediCore Hospital  ·  How the website works")
    canvas.setFillColor(CREAM)
    canvas.rect(0, 0, A4[0], 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(16 * mm, 5 * mm, "English + Hinglish  ·  For viva / demo  ·  Not a code dump")
    canvas.drawRightString(A4[0] - 16 * mm, 5 * mm, f"Page {doc.page}")
    canvas.restoreState()


def cover_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(SIDE)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.roundRect(18 * mm, 28 * mm, A4[0] - 36 * mm, A4[1] - 56 * mm, 10, fill=0, stroke=1)
    canvas.setFillColor(colors.HexColor("#9FCCC6"))
    canvas.setFont("Helvetica", 9)
    canvas.drawCentredString(A4[0] / 2, 18 * mm, "English + Hinglish  ·  Viva / demo  ·  MediCore 2026")
    canvas.restoreState()


def build():
    pages = draw_pages_map()
    flow = draw_flow_map()
    roles = draw_roles_map()
    s = styles()
    story = []

    # Cover content sits on dark page via onFirstPage drawing + white text table
    cover_tbl = Table(
        [[Paragraph("MediCore Hospital", s["cover"])],
         [Paragraph("How the website works", s["cover"])],
         [Spacer(1, 8)],
         [Paragraph("Full explanation for viva, demo and teachers<br/>English + Hinglish  ·  Every tab  ·  Server &amp; database  ·  Mindmaps", s["coversub"])],
         [Spacer(1, 16)],
         [Paragraph("Project folder: Desktop/MediCore-Pages<br/>Live (if deployed): https://medicore-hospital.onrender.com<br/>This Mac: http://127.0.0.1:5000", s["coversub"])]],
        colWidths=[150 * mm],
    )
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SIDE),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(Spacer(1, 70 * mm))
    story.append(cover_tbl)
    story.append(PageBreak())

    story.append(Paragraph("1. Overview", s["h1"]))
    story.append(Paragraph(
        "MediCore is a <b>hospital website</b>. Visitors can read about the hospital and book a slot. "
        "Staff and admin sign in to run the floor: patients, doctors, beds, pharmacy, scans and bills. "
        "A patient signs in and sees <b>only their own file</b>. Nothing is fake-on-the-screen-only: when you click Save, the server writes a database.",
        s["body"],
    ))
    story.append(hinglish(s, "",
        "Yeh project ek hospital ki website hai. Bahar se koi bhi Home, About, Departments dekh sakta hai aur Book se slot maang sakta hai. "
        "Staff/Admin login karke poora hospital chalata hai. Patient login karke sirf apni file dekhta hai. Save dabane par data database mein likh jata hai — sirf dikhawa nahi hai."))

    story.append(Paragraph("What you can say in one breath", s["h2"]))
    story.append(bullets(s, [
        "It is a city hospital site (Mumbai story) with a public face and a private console.",
        "Three doors: Staff, Patient, Admin — same login page, different home after sign-in.",
        "Public Book creates a <b>Pending</b> appointment; staff Confirm it.",
        "Hindi toggle changes labels; medical IDs stay as DOC-1001 / P-4821.",
        "This Mac can run it at login. GitHub stores code. Render can host the live URL.",
    ]))
    story.append(hinglish(s, "",
        "Ek saans mein: public pages + login ke baad console. Teen role. Book se pending appointment. Hindi button se bhasha. Mac par local, GitHub par code, Render par live site."))

    story.append(Paragraph("2. Server — kya hai, kahan chaltaa hai", s["h1"]))
    story.append(Paragraph(
        "The <b>server</b> is a Python program named <b>Flask</b> (<font face='Courier'>app.py</font>). It waits for the browser. "
        "If you ask for a page like Home, it sends the HTML file. If you ask for <font face='Courier'>/api/login</font> or "
        "<font face='Courier'>/api/store/patients</font>, it reads or writes the database and sends JSON.",
        s["body"],
    ))
    story.append(Paragraph(
        "On <b>this Mac</b> the server can start when you log in (LaunchAgent). You open http://127.0.0.1:5000. "
        "On the <b>internet</b>, Render runs <b>gunicorn</b> (a production runner for Flask) inside a Docker container. "
        "GitHub does <b>not</b> run the hospital — it only stores the files. Render reads GitHub and starts the server.",
        s["body"],
    ))
    story.append(hinglish(s, "",
        "Server Matlab ek program jo browser ki request sunta hai. Flask = hamara server. Mac par localhost:5000. "
        "Internet par Render gunicorn se chalata hai. GitHub sirf copy rakhta hai, website nahi chalaata."))

    story.append(Paragraph("How a request travels", s["h2"]))
    story.append(RLImage(str(flow), width=170 * mm, height=95 * mm))
    story.append(Paragraph("Figure — click se lekar screen update tak.", s["tiny"]))
    story.append(hinglish(s, "",
        "Aap click karte ho → Flask decide karta hai page dena hai ya API → database padhta/likhta hai → JSON ya HTML wapas → screen naya data dikhati hai."))

    story.append(Paragraph("3. Database — kahan data rehta hai", s["h1"]))
    story.append(Paragraph(
        "The database is the hospital’s notebook. Two flavours, same idea:",
        s["body"],
    ))
    story.append(bullets(s, [
        "<b>This Mac:</b> if MySQL is running, Flask uses MySQL (database name <font face='Courier'>medicore</font>). If not, it uses a file <font face='Courier'>medicore-live.db</font> (SQLite).",
        "<b>Render (live):</b> always SQLite inside the service. No separate MySQL to install.",
        "Tables include: <b>users</b> (logins), <b>doctors, patients, appointments, pharmacy, rooms, invoices, diagnostics, alerts</b>.",
        "Staff screens load everything once from <font face='Courier'>GET /api/bootstrap</font>, then each Save is <font face='Courier'>PUT /api/store/&lt;name&gt;</font> with the full list.",
        "Patient screens use <font face='Courier'>GET /api/patient/home</font> so other patients’ rows never arrive in the browser.",
    ]))
    story.append(hinglish(s, "",
        "Database hospital ki copy hai. Mac par MySQL ya SQLite file. Render par SQLite. Users table se login. Patients/doctors/appointments alag tables. "
        "Staff Save = poori list server ko. Patient ko sirf uski row milti hai."))

    db_rows = [[
        Paragraph("<b>Table</b>", s["li"]),
        Paragraph("<b>English</b>", s["li"]),
        Paragraph("<b>Hinglish</b>", s["li"]),
    ], [
        Paragraph("users", s["li"]), Paragraph("IDs and password hashes (Staff / Patient / Admin)", s["li"]),
        Paragraph("Kaun login kar sakta hai", s["li"]),
    ], [
        Paragraph("patients", s["li"]), Paragraph("Name, age, ward, doctor, status", s["li"]),
        Paragraph("Meri file / saari files (staff)", s["li"]),
    ], [
        Paragraph("doctors", s["li"]), Paragraph("Roster, department, on/off duty", s["li"]),
        Paragraph("Doctor list", s["li"]),
    ], [
        Paragraph("appointments", s["li"]), Paragraph("OPD slots and status (Pending → Confirmed)", s["li"]),
        Paragraph("Token / time", s["li"]),
    ], [
        Paragraph("rooms", s["li"]), Paragraph("Beds, occupancy, tariff", s["li"]),
        Paragraph("Ward allotment", s["li"]),
    ], [
        Paragraph("invoices", s["li"]), Paragraph("Bills, UPI/card/cash, paid or due", s["li"]),
        Paragraph("Bill", s["li"]),
    ], [
        Paragraph("pharmacy", s["li"]), Paragraph("Medicine name, batch, stock", s["li"]),
        Paragraph("Dawai stock", s["li"]),
    ], [
        Paragraph("diagnostics", s["li"]), Paragraph("ECG, CT, MRI slots", s["li"]),
        Paragraph("Scan / report", s["li"]),
    ], [
        Paragraph("alerts", s["li"]), Paragraph("SMS / email / WhatsApp log (demo unless keys added)", s["li"]),
        Paragraph("Message register", s["li"]),
    ]]
    db = Table(db_rows, colWidths=[28 * mm, 72 * mm, 70 * mm], repeatRows=1)
    db.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SIDE),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("BACKGROUND", (0, 1), (-1, -1), WHITE),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, CREAM]),
    ]))
    story.append(Spacer(1, 6))
    story.append(db)
    story.append(Spacer(1, 8))

    story.append(Paragraph("4. Who signs in (roles)", s["h1"]))
    story.append(RLImage(str(roles), width=170 * mm, height=76 * mm))
    story.append(Paragraph(
        "One Sign in page. Three cards: Staff, Patient, Admin. You type ID and password only — <b>no OTP step</b>, and <b>no sample IDs in the boxes</b> (privacy). "
        "Wrong card + right password still fails (a doctor ID will not open on the Patient card).",
        s["body"],
    ))
    story.append(hinglish(s, "",
        "Login page par teen card. Sirf ID aur password. OTP nahi. Box mein example ID nahi likhe. Galat card choose kiya to login nahi hoga."))

    story.append(Paragraph("Presenter-only demo IDs (not shown on the website)", s["h2"]))
    demo = [[
        Paragraph("<b>Role</b>", s["li"]), Paragraph("<b>ID</b>", s["li"]),
        Paragraph("<b>Password</b>", s["li"]), Paragraph("<b>Lands on</b>", s["li"]),
    ], [
        Paragraph("Staff", s["li"]), Paragraph("DOC-1001", s["li"]),
        Paragraph("123456", s["li"]), Paragraph("Dashboard", s["li"]),
    ], [
        Paragraph("Patient", s["li"]), Paragraph("P-4821", s["li"]),
        Paragraph("Aarav21", s["li"]), Paragraph("Patient portal", s["li"]),
    ], [
        Paragraph("Admin", s["li"]), Paragraph("ADMIN-1000", s["li"]),
        Paragraph("Admin24", s["li"]), Paragraph("Dashboard + Staff/Patients/Admin switch", s["li"]),
    ]]
    dt = Table(demo, colWidths=[32 * mm, 36 * mm, 32 * mm, 70 * mm], repeatRows=1)
    dt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SIDE),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, CREAM]),
    ]))
    story.append(dt)
    story.append(Paragraph("Say these aloud in a viva; do not print them on the login screen.", s["tiny"]))
    story.append(PageBreak())

    story.append(Paragraph("5. Mindmap of every page", s["h1"]))
    story.append(RLImage(str(pages), width=170 * mm, height=116 * mm))
    story.append(Paragraph("Figure — teen ghar: public, staff console, patient portal.", s["tiny"]))
    story.append(hinglish(s, "",
        "Pehle bina login public pages. Login ke baad staff ko left menu milta hai. Patient ko alag simple portal milta hai. Admin upar se view badal sakta hai."))

    story.append(Paragraph("6. Public pages — tab by tab", s["h1"]))

    public = [
        ("Home",
         "First impression. Emergency strip, hero, departments preview, visiting hours, photos of campus life. Buttons to Patient login, Staff/Admin, Contact. Hindi toggle in the header.",
         "Sabse pehli photo-wali page. Emergency number, beds, departments ka preview. Login ke buttons. Header mein हिन्दी."),
        ("About",
         "Why the hospital exists, values, lab/ICU story photos. No login needed.",
         "Hospital ki kahani aur values. Login ki zaroorat nahi."),
        ("Departments",
         "Eight cards: Emergency, Cardiology, Maternity, Paediatrics, Orthopaedics, Diagnostics, Neurology, Oncology. Each card has its own photo (not repeated).",
         "Aath vibhag. Har card ki alag photo. Emergency 24×7, baaki OPD."),
        ("Facilities",
         "Beds, ICU, pharmacy, ambulance, cafeteria. Explains campus, not the console.",
         "Suvidhaayein: bed, ICU, canteen. Console nahi, campus hai."),
        ("Book",
         "Form: name, mobile, department, date, time. Sends POST /api/public/appointment. Status starts as Pending. Staff later Confirm. No account needed.",
         "Bina login slot maango. Pending rehta hai jab tak staff Confirm na kare."),
        ("Contact",
         "Address (Sion–Bandra Link Road story), emergency 022 2416 2400, ambulance 108, hours, how a patient ID is issued at reception.",
         "Pata, phone, visiting hours. Patient ID reception par milti hai."),
        ("Sign in",
         "Staff / Patient / Admin cards, empty ID and password, Continue. Success → dashboard or patient portal. Forgot password tells you to ask the administrator (no OTP screen).",
         "Teen card, khali boxes, Continue. OTP nahi. Password bhool gaye to admin se kaho."),
    ]
    for title, en, hi in public:
        story.append(Paragraph(title, s["h2"]))
        story.append(Paragraph(en, s["body"]))
        story.append(hinglish(s, "", hi))

    story.append(Paragraph("7. After login — Staff / Admin tabs", s["h1"]))
    story.append(Paragraph(
        "Left sidebar is the main menu. Top bar has the page title, a Live pill, your name, Hindi/English, Sign out. "
        "Admin also sees <b>Staff | Patients | Admin</b> (this used to say Combined; it now says Admin). "
        "Staff view = hospital floor. Patients view = portal list. Admin view = both.",
        s["body"],
    ))
    story.append(hinglish(s, "",
        "Left menu se saare desks. Upar Live, naam, हिन्दी, Sign out. Admin ke paas teen button: Staff, Patients, Admin. Pehle Combined likha tha, ab Admin likha hai."))

    staff_tabs = [
        ("Dashboard",
         "Live KPIs: active patients, doctors on duty, today’s appointments, free beds. Today’s queue, revenue share, recently admitted, latest alerts. Jump-off page after staff login.",
         "Pehla screen. Aaj ke numbers: patients, doctors, beds, queue. Yahan se doosri tabs kholte ho."),
        ("Patients",
         "Search and filter. Register patient (creates a portal ID + password pattern). Edit name, dept, doctor, status (Admitted / Observation / Discharged). Links to Ward and Bill.",
         "Naya patient jodo ya purana badlo. Status Admitted/Discharge. Ward aur bill ki shortcuts."),
        ("Doctors",
         "Roster. Add doctor, set off duty, optional staff login (DOC-…). You cannot delete your own login.",
         "Doctor list. Off duty, naya doctor. Apna login khud delete nahi kar sakte."),
        ("Appointments",
         "Book from the desk (starts Confirmed) or see public Book rows as Pending. Confirm / Check in / Cancel. Confirm can log an SMS/WhatsApp reminder row.",
         "Desk se booking Confirmed. Website Book se Pending. Confirm/Cancel yahi se."),
        ("Pharmacy",
         "Medicine name, batch, stock vs minimum. Add stock. Low stock is visible in KPIs.",
         "Dawai, batch, kitni strips. Kam stock dikhta hai."),
        ("Ward Allotment",
         "Rooms: ICU, private, general, maternity. Allot a named patient to a free bed, discharge, add a room. Occupancy bars.",
         "Room aur bed. Patient ko bed do, discharge karo."),
        ("Diagnostics",
         "Schedule ECG/CT/MRI etc. Mark Done when the report is ready (can log ‘report ready’).",
         "Scan slot. Done matlab report ready."),
        ("Payments",
         "Create invoice, collect (UPI/card/cash/insurance), refund, print-style receipt. Today’s collections vs dues.",
         "Bill banao, wasooli, refund, receipt."),
        ("Reports",
         "Printable summary of today’s work for a file or notice board. Uses the same live data.",
         "Aaj ka summary print karne ke liye."),
        ("Email & SMS",
         "Message register. Templates can be queued. Without Twilio/Gmail keys, rows stay Queued/demo. With keys, the same screen can send for real.",
         "Message ki copy. Abhi demo log. Real SMS ke liye baad mein Twilio."),
    ]
    for title, en, hi in staff_tabs:
        story.append(Paragraph(title, s["h2"]))
        story.append(Paragraph(en, s["body"]))
        story.append(hinglish(s, "", hi))

    story.append(Paragraph("8. Patient portal", s["h1"]))
    story.append(Paragraph(
        "After P-4821 (or any patient ID) signs in: greeting, own details, reports table, bills with Pay, appointments. "
        "Pay opens UPI / card / net banking. On this project it marks the invoice Paid in the database (demo checkout unless Razorpay keys exist). "
        "Another patient cannot open this file.",
        s["body"],
    ))
    story.append(hinglish(s, "",
        "Patient ko sirf apni details, report, bill, appointment dikhti hai. Pay se bill Paid ho jata hai (demo). Doosre patient ki file nahi khulti."))

    story.append(Paragraph("9. Click-along demo (use this order)", s["h1"]))
    story.append(bullets(s, [
        "Open Home — show emergency strip, photos, Hindi button.",
        "Open Book — submit a test name. Tell them it is Pending.",
        "Sign in as Staff DOC-1001 / 123456 — Dashboard numbers.",
        "Appointments — find the Pending row — Confirm.",
        "Patients — register someone — show new ID.",
        "Ward — allot a bed. Payments — collect a due bill.",
        "Sign out. Sign in as Patient P-4821 / Aarav21 — only Aarav’s file.",
        "Sign in as Admin ADMIN-1000 / Admin24 — show Staff / Patients / Admin switch.",
    ]))
    story.append(hinglish(s, "",
        "Demo order: Home → Book (pending) → Staff login → Confirm appointment → naya patient → bed → bill → Patient login (sirf apni file) → Admin login (teen buttons)."))

    story.append(Paragraph("10. Extra features you can mention", s["h1"]))
    story.append(bullets(s, [
        "Hindi / English on public pages and console chrome.",
        "Logo in the header (teal cross by default; options B/C/D exist as logo-b/c/d).",
        "Photos: unique per public section, fitted in frames; <b>no photos inside the after-login menu</b>.",
        "Lockout after too many wrong passwords (short wait).",
        "Live URL on Render; local auto-start on this Mac.",
    ]))
    story.append(hinglish(s, "",
        "Hindi button, logo, alag-alag photos public pages par, login ke baad menu mein photo nahi, galat password par thodi der lock, Mac + Render."))

    story.append(Paragraph("11. Two-minute viva script", s["h1"]))
    story.append(Paragraph("<b>English</b>", s["h2"]))
    story.append(Paragraph(
        "This is MediCore, a hospital website. Outside, anyone can read about departments and book a slot without an account. "
        "Staff sign in and get a live console: patients, beds, pharmacy, bills. A patient signs in and sees only their file. "
        "The server is Flask; the database is MySQL on this Mac or SQLite on Render. Save writes to the database. "
        "GitHub holds the code; Render can host it live.",
        s["body"],
    ))
    story.append(hinglish(s, "",
        "Yeh MediCore hai — hospital website. Bahar se departments padho, bina account Book karo. Staff login karke poora floor chalata hai. "
        "Patient sirf apni file dekhta hai. Server Flask hai. Database Mac par MySQL ya live par SQLite. Save asli data likhta hai. "
        "Code GitHub par, live site Render par."))

    story.append(Paragraph("If something looks stuck on the live URL", s["h2"]))
    story.append(Paragraph(
        "Free Render sleeps. Wait about 30 seconds on the first open. Use one gunicorn worker with SQLite so pages do not freeze. "
        "After you push code, click Manual Deploy → Clear build cache on Render.",
        s["body"],
    ))
    story.append(hinglish(s, "",
        "Pehli baar live link dheere khul sakti hai — 30 second wait. Deploy ke baad Render par Clear build cache karo."))

    story.append(Spacer(1, 12))
    story.append(Paragraph("End of guide  ·  MediCore Hospital  ·  Explain with the two mindmaps above.", s["center"]))

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=20 * mm,
        bottomMargin=16 * mm,
        title="MediCore Hospital — How the website works",
        author="MediCore project",
    )
    doc.build(story, onFirstPage=cover_page, onLaterPages=header_footer)
    print("Wrote", OUT)


if __name__ == "__main__":
    build()
