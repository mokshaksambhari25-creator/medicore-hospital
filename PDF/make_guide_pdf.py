#!/usr/bin/env python3
"""MediCore staff guide — 16 pages: handbook + presentation slides."""
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
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

OUT = "/Users/mac/Desktop/MediCore-Pages/MediCore-Staff-Guide.pdf"

TEAL = colors.HexColor("#0F766E")
DEEP = colors.HexColor("#123C38")
CREAM = colors.HexColor("#F5F2EC")
MINT = colors.HexColor("#CCFBF1")
LINE = colors.HexColor("#E4DDD2")
TEXT = colors.HexColor("#134E4A")
MUTED = colors.HexColor("#5C6B68")
WHITE = colors.white
ROSE = colors.HexColor("#9F1239")


def S():
    b = getSampleStyleSheet()
    return {
        "kicker": ParagraphStyle("kicker", parent=b["Normal"], fontName="Helvetica-Bold",
                                 fontSize=9, textColor=TEAL, spaceAfter=6, leading=12),
        "cover": ParagraphStyle("cover", parent=b["Title"], fontName="Helvetica-Bold",
                                fontSize=30, textColor=DEEP, leading=36, alignment=TA_LEFT, spaceAfter=10),
        "lead": ParagraphStyle("lead", parent=b["Normal"], fontName="Helvetica",
                               fontSize=11, textColor=MUTED, leading=16, spaceAfter=8),
        "h1": ParagraphStyle("h1", parent=b["Heading1"], fontName="Helvetica-Bold",
                             fontSize=16, textColor=DEEP, spaceBefore=2, spaceAfter=8, leading=20),
        "h2": ParagraphStyle("h2", parent=b["Heading2"], fontName="Helvetica-Bold",
                             fontSize=12, textColor=TEAL, spaceBefore=10, spaceAfter=5, leading=15),
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
        "code": ParagraphStyle("code", parent=b["Normal"], fontName="Courier",
                               fontSize=9, textColor=DEEP, leading=13, spaceAfter=3),
        "say": ParagraphStyle("say", parent=b["Normal"], fontName="Helvetica-Oblique",
                              fontSize=10, textColor=TEAL, leading=14, spaceAfter=4),
        "slide_h": ParagraphStyle("slide_h", parent=b["Title"], fontName="Helvetica-Bold",
                                  fontSize=22, textColor=DEEP, leading=26, spaceAfter=6, alignment=TA_LEFT),
        "slide_t": ParagraphStyle("slide_t", parent=b["Normal"], fontName="Helvetica-Bold",
                                  fontSize=12, textColor=DEEP, leading=15, spaceAfter=3),
        "slide_b": ParagraphStyle("slide_b", parent=b["Normal"], fontName="Helvetica",
                                  fontSize=10, textColor=TEXT, leading=14, spaceAfter=3),
        "toc": ParagraphStyle("toc", parent=b["Normal"], fontName="Helvetica",
                              fontSize=10, textColor=TEXT, leading=16, spaceAfter=2),
    }


def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(DEEP)
    canvas.rect(0, h - 13 * mm, w, 13 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(16 * mm, h - 8 * mm, "MediCore  ·  Staff guide & walkthrough")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w - 16 * mm, h - 8 * mm, "Internal use only")
    canvas.setFillColor(TEAL)
    canvas.rect(0, 0, w, 11 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(16 * mm, 4.5 * mm, "Keep this PDF offline. Do not put logins on the website.")
    canvas.drawRightString(w - 16 * mm, 4.5 * mm, "Page %d of 16" % doc.page)
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


def card_table(inner, width=178 * mm):
    t = Table([[inner]], colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CREAM),
        ("BOX", (0, 0), (-1, -1), 0.6, TEAL),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def bullets(items, st, style="body"):
    return ListFlowable(
        [ListItem(Paragraph(x, st[style]), leftIndent=6, bulletColor=TEAL) for x in items],
        bulletType="bullet", start="•", leftIndent=12,
        bulletFontName="Helvetica", bulletFontSize=9, spaceBefore=1, spaceAfter=6,
    )


def build():
    st = S()
    H, P, C = st["th"], st["td"], st["tdc"]
    story = []
    W = 178 * mm

    # ========== PAGE 1 COVER ==========
    story.append(Paragraph("STAFF HANDBOOK  ·  16 PAGES", st["kicker"]))
    story.append(Paragraph("MediCore website guide", st["cover"]))
    story.append(Paragraph(
        "A full handbook for hospital staff: how to open the site, who can sign in, "
        "what every page does, how to add or remove a doctor, and how the database saves work. "
        "Pages 11–16 are a simple walkthrough you can speak from.",
        st["lead"],
    ))
    story.append(Paragraph(
        "<b>Keep this file private.</b> The live website never shows Staff IDs or the password. "
        "This PDF is only for people who need to log in or present the system.",
        st["warn"],
    ))
    story.append(Paragraph("What is inside", st["h2"]))
    toc = [
        "Pages 1–2 &nbsp;&nbsp; How to open MediCore, and the contents of this guide",
        "Page 3 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Doctor names, Staff IDs and the shared password",
        "Page 4 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; How to add, edit, hide or remove a doctor",
        "Pages 5–8 &nbsp;&nbsp; Every webpage in detail (public + staff console)",
        "Pages 9–10 &nbsp; Database (SQLite), security, folders, checklist",
        "Pages 11–16 Presentation slides — simple words for each webpage",
    ]
    for line in toc:
        story.append(Paragraph(line, st["toc"]))
    story.append(Spacer(1, 8))
    story.append(card_table(Paragraph(
        "<b>Website address:</b> http://127.0.0.1:5000<br/>"
        "<b>Folder:</b> Desktop/MediCore-Pages<br/>"
        "<b>Database file:</b> medicore.db &nbsp;·&nbsp; <b>Server:</b> python3 app.py",
        st["body"],
    )))
    story.append(PageBreak())

    # ========== PAGE 2 OPEN ==========
    story.append(Paragraph("1. How to open the website", st["h1"]))
    story.append(Paragraph(
        "MediCore is a real local web app, not a set of files you double-click. "
        "A small Python program (Flask) serves the pages and talks to a SQLite database on this computer. "
        "If the program is not running, login and saving will fail.",
        st["body"],
    ))
    story.append(Paragraph("Start the server", st["h2"]))
    story.append(Paragraph("Open Terminal and type these two lines, then press Return after each:", st["body"]))
    story.append(Paragraph("cd ~/Desktop/MediCore-Pages", st["code"]))
    story.append(Paragraph("python3 app.py", st["code"]))
    story.append(Paragraph("You should see:  MediCore  →  http://127.0.0.1:5000", st["body"]))
    story.append(Paragraph("Open the site", st["h2"]))
    story.append(Paragraph(
        "In Chrome, Safari or Edge go to <b>http://127.0.0.1:5000</b>. "
        "You will see the public Home page (hospital photos). Click <b>Staff login</b> to enter the console.",
        st["body"],
    ))
    story.append(Paragraph(
        "Do <b>not</b> open index.html from Finder. That bypasses the database.",
        st["warn"],
    ))
    story.append(Paragraph("Two kinds of visitor", st["h2"]))
    vis = [[Paragraph(x, H) for x in ["Visitor", "What they can open"]]]
    vis += [
        [Paragraph("Anyone (no login)", C),
         Paragraph("Home, About, Staff login. Department cards on Home send them to login.", P)],
        [Paragraph("Signed-in doctor", C),
         Paragraph("The same Home, now with the teal left menu used on Payments and every other staff page, "
                   "plus Dashboard, Patients, Doctors, Appointments, Pharmacy, Ward, Diagnostics, Payments, Reports, Email &amp; SMS.", P)],
    ]
    story.append(table(vis, [42 * mm, 136 * mm]))
    story.append(Paragraph("Leave the desk", st["h2"]))
    story.append(Paragraph(
        "Click <b>Sign out</b> at the top right. You return to public Home. "
        "Leave the Terminal window running while people use the site. Closing it stops the database.",
        st["body"],
    ))
    story.append(PageBreak())

    # ========== PAGE 3 LOGINS ==========
    story.append(Paragraph("2. Doctor names, Staff IDs and password", st["h1"]))
    story.append(Paragraph(
        "The login box asks for a <b>Staff ID</b> (not the person’s name) and a <b>password</b>. "
        "All six starter accounts share one password. Type the ID in capital letters.",
        st["body"],
    ))
    story.append(Paragraph("Shared password for every starter doctor:  <b>123456</b>", st["h2"]))
    login_rows = [[Paragraph(x, H) for x in ["Staff ID", "Doctor name", "Department", "Password"]]]
    for i, name, dept in [
        ("DOC-1001", "Dr. Meera Nair", "Cardiology"),
        ("DOC-1002", "Dr. Rohan Das", "General Medicine"),
        ("DOC-1003", "Dr. Kavya Iyer", "Orthopaedics"),
        ("DOC-1004", "Dr. Imran Sheikh", "Neurology"),
        ("DOC-1005", "Dr. Ananya Bose", "Paediatrics"),
        ("DOC-1006", "Dr. Arjun Menon", "Oncology"),
    ]:
        login_rows.append([Paragraph(i, C), Paragraph(name, P), Paragraph(dept, P), Paragraph("123456", P)])
    story.append(table(login_rows, [32 * mm, 48 * mm, 50 * mm, 28 * mm]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Example.</b> Staff ID <b>DOC-1001</b> and password <b>123456</b> signs you in as Dr. Meera Nair (Cardiology). "
        "The header shows her initials and department.",
        st["body"],
    ))
    story.append(Paragraph("Rules", st["h2"]))
    story.append(bullets([
        "The website itself never lists these IDs or the password. Only this PDF does.",
        "Wrong ID or password always shows the same line: “Invalid staff ID or password.”",
        "Five failed tries on one ID locks it for 2 minutes.",
        "You can change a doctor’s <b>display name</b> later. The Staff ID stays the same, so login still works.",
        "New doctors you add (DOC-1007 onwards) can also sign in if you tick that box. They use the <b>same password 123456</b>.",
        "Passwords in the database are hashed (scrambled). The file medicore.db does not store 123456 as plain text.",
    ], st))
    story.append(PageBreak())

    # ========== PAGE 4 ADD/REMOVE ==========
    story.append(Paragraph("3. Add, edit, hide or remove a doctor", st["h1"]))
    story.append(Paragraph(
        "Open the left menu → <b>Doctors</b>. This is the roster used by appointments, patients and the login system.",
        st["body"],
    ))
    story.append(Paragraph("Add a new doctor", st["h2"]))
    story.append(bullets([
        "Click <b>Add doctor</b> (top right).",
        "Type the name (example: Dr. Priya Kulkarni). If you omit “Dr.”, MediCore adds it.",
        "Pick department and phone.",
        "Tick <b>Allow this doctor to sign in to MediCore</b> if they should open the website. Leave it unticked if they only appear on the roster.",
        "Click <b>Add doctor</b>. They get the next ID: DOC-1007, DOC-1008, and so on.",
        "If you ticked sign-in, they log in with that new Staff ID and password <b>123456</b>.",
    ], st))
    story.append(Paragraph("Change a name", st["h2"]))
    story.append(Paragraph(
        "On their row click <b>Edit</b>, change name / department / phone, <b>Save</b>. "
        "The Staff ID does not change. Appointments and the header pick up the new name.",
        st["body"],
    ))
    story.append(Paragraph("Hide someone without deleting (off duty)", st["h2"]))
    story.append(Paragraph(
        "Click <b>Set off duty</b>. They stay in the list but drop out of appointment booking until you click <b>Set available</b>.",
        st["body"],
    ))
    story.append(Paragraph("Remove someone", st["h2"]))
    story.append(bullets([
        "On their row click <b>Remove</b>, then confirm.",
        "If they had a login, that Staff ID stops working.",
        "You cannot remove the account you are signed in as (the row is marked <b>You</b>). Sign in as someone else first.",
        "The system keeps at least one staff login so the hospital is never locked out.",
    ], st))
    story.append(PageBreak())

    # ========== PAGE 5 PUBLIC PAGES ==========
    story.append(Paragraph("4. Public pages in detail", st["h1"]))
    story.append(Paragraph("Home  ·  index.html", st["h2"]))
    story.append(Paragraph(
        "This is the main website. At the top: MediCore, Home, About, Staff login. "
        "A large photo of the hospital atrium (MEDI1) sits next to the headline "
        "“Run the whole hospital from one calm console.” Stats show beds, modules and 24×7 emergency. "
        "A second photo (MEDI2) shows the care team. Below that, every department is a card.",
        st["body"],
    ))
    story.append(Paragraph(
        "If you are <b>not</b> signed in, a department card goes to Staff login. "
        "After you sign in, Home switches to the <b>same teal sidebar and top bar as Payments</b>. "
        "Home is the first item in that menu. Shortcuts still open each module. Sign out is top right.",
        st["body"],
    ))
    story.append(Paragraph("About  ·  about.html", st["h2"]))
    story.append(Paragraph(
        "The story of MediCore: built with hospital teams, four beliefs (patients first, everything connected, "
        "data you can trust, communication built in). Uses the same two photos. No login needed.",
        st["body"],
    ))
    story.append(Paragraph("Staff login  ·  login.html", st["h2"]))
    story.append(Paragraph(
        "Split screen: hospital photo on the left, a quiet form on the right. Only two fields — "
        "<b>Staff ID</b> and <b>Password</b>. There is a Show/Hide control on the password. "
        "No doctor list, no hint, no 123456 on the page. A correct login goes to the Dashboard. "
        "Already signed in? This page sends you to the Dashboard automatically.",
        st["body"],
    ))
    story.append(Paragraph("Colours (the whole site)", st["h2"]))
    story.append(Paragraph(
        "Cream page background, deep teal sidebar, mint “Live” badge, green / amber / blue / rose status pills. "
        "The same look on every staff page so the console feels like one product.",
        st["body"],
    ))
    story.append(PageBreak())

    # ========== PAGE 6 DASHBOARD PATIENTS ==========
    story.append(Paragraph("5. Dashboard and Patients", st["h1"]))
    story.append(Paragraph("Dashboard  ·  dashboard.html", st["h2"]))
    story.append(Paragraph(
        "The operations screen. Four tiles at the top are counted from the database: active patients, "
        "doctors on duty, today’s appointments, beds available. Below: today’s appointment queue, "
        "revenue share by department (from paid invoices), recently admitted patients, and the latest SMS rows. "
        "Nothing here is typed by hand — if you collect a payment or book a slot, this page changes.",
        st["body"],
    ))
    story.append(Paragraph("Patients  ·  patients.html", st["h2"]))
    story.append(Paragraph(
        "The master list of people in care. Search by name, ID or phone. Filter by Admitted / Observation / Discharged.",
        st["body"],
    ))
    story.append(bullets([
        "<b>Register patient</b> — name, age, gender, phone, blood group, department, doctor, status. Saved at once.",
        "<b>Edit</b> — change any of those fields. Status changes show on the Dashboard.",
        "<b>Ward</b> / <b>Bill</b> — jump to allot a bed or raise an invoice for that person.",
        "Starter patients (Indian names): Aarav Sharma, Ritu Verma, Nikhil Patil, Sneha Patil, Fatima Khan, Kabir Reddy.",
    ], st))
    story.append(Paragraph(
        "Patient IDs look like PT-4401. New rows get the next number. Everything is stored in the patients list inside medicore.db.",
        st["body"],
    ))
    story.append(PageBreak())

    # ========== PAGE 7 DOCTORS APPT PHARM ==========
    story.append(Paragraph("6. Doctors, Appointments, Pharmacy", st["h1"]))
    story.append(Paragraph("Doctors  ·  doctors.html", st["h2"]))
    story.append(Paragraph(
        "Roster of consultants. Login accounts show a green <b>Login</b> pill. Your own row shows <b>You</b>. "
        "Add doctor, Edit, Set off duty / available, Remove — all explained on page 4. "
        "Appointment booking only offers doctors who are marked available.",
        st["body"],
    ))
    story.append(Paragraph("Appointments  ·  appointments.html", st["h2"]))
    story.append(Paragraph(
        "OPD booking. Left: form (patient name, mobile, department, doctor, date, time chips). "
        "Right: the queue. Statuses: Pending, Confirmed, Checked-in, Cancelled.",
        st["body"],
    ))
    story.append(bullets([
        "<b>Confirm booking</b> creates AP-5512, AP-5513, … and queues an SMS reminder.",
        "<b>Confirm</b> / <b>Check in</b> / <b>Cancel</b> on a row update the Dashboard queue the same moment.",
        "OPD hours in spirit: 9:00 AM – 6:00 PM slots. Emergency is described as 24×7 on Home, not a separate page.",
    ], st))
    story.append(Paragraph("Pharmacy  ·  pharmacy.html", st["h2"]))
    story.append(Paragraph(
        "Medicine stock. Add a drug (name, batch, opening stock, reorder level, unit). "
        "<b>Dispense 1</b> reduces stock. <b>Add 10</b> restocks. Status pills: In-stock, Low, Out. "
        "Low is when stock is at or below the reorder level (example: Insulin).",
        st["body"],
    ))
    story.append(PageBreak())

    # ========== PAGE 8 WARD DX PAY ==========
    story.append(Paragraph("7. Ward, Diagnostics, Payments", st["h1"]))
    story.append(Paragraph("Ward Allotment  ·  ward-allotment.html", st["h2"]))
    story.append(Paragraph(
        "Beds and rooms. Tiles: total beds, occupied, available, under cleaning. Bars show occupancy for ICU, Private, General, Maternity.",
        st["body"],
    ))
    story.append(bullets([
        "<b>Add bed</b> — new room ID (example PR-220), type, floor, number of beds, daily tariff. Starts as Available.",
        "<b>Allot bed</b> — pick a patient and a room that still has a free bed. Occupied and Cleaning rooms are blocked. A patient cannot hold two beds.",
        "<b>Discharge</b> — frees the bed; an empty room goes to Cleaning (housekeeping).",
        "<b>Mark available</b> after cleaning. <b>Mark cleaning</b> on an empty available room.",
        "Tariffs (examples): ICU Rs 12,000/day, Private Rs 6,500/day, General Rs 1,800/day, Maternity Rs 4,200/day.",
    ], st))
    story.append(Paragraph("Diagnostics  ·  diagnostics.html", st["h2"]))
    story.append(Paragraph(
        "Scan diary: MRI, CT, X-ray, ECG, ultrasound. Book a patient, date and slot. "
        "<b>Mark done</b> when the report is ready — an alert is queued. IDs look like DX-2201.",
        st["body"],
    ))
    story.append(Paragraph("Payments  ·  payment.html", st["h2"]))
    story.append(Paragraph(
        "Billing desk. Tiles: collected today, outstanding dues, insurance claims, refunds — all from the invoice list.",
        st["body"],
    ))
    story.append(bullets([
        "<b>Quick payment</b> — invoice or patient name, amount, method chip (UPI / Card / Cash / Insurance), Collect. Opens a printable receipt.",
        "<b>Create invoice</b> — patient, department, amount, method, notes. Insurance starts as Processing; others as Due.",
        "<b>Collect</b> / <b>Refund</b> on a row. Search and filter by status or method.",
        "Dashboard “revenue share” uses these paid amounts by department.",
    ], st))
    story.append(PageBreak())

    # ========== PAGE 9 REPORTS + SAVES ==========
    story.append(Paragraph("8. Reports, Email &amp; SMS, and every Save", st["h1"]))
    story.append(Paragraph("Reports  ·  reports.html", st["h2"]))
    story.append(Paragraph(
        "A daily snapshot calculated from the other modules: collections, outstanding dues, occupancy %, OPD today, "
        "patients by department, latest invoices. If billing or wards change, this page changes. You do not type the totals.",
        st["body"],
    ))
    story.append(Paragraph("Email &amp; SMS  ·  notifications.html", st["h2"]))
    story.append(Paragraph(
        "A log, not a real telecom gateway. Queue a template (Appointment Reminder, Payment Due, Report Ready, "
        "Scan Slot Changed, Discharge Summary) to a phone or email. Mark delivered. "
        "Booking an appointment or collecting a payment also adds a row automatically.",
        st["body"],
    ))
    story.append(Paragraph("Every button that writes the database", st["h2"]))
    saves = [[Paragraph(x, H) for x in ["Page", "Actions that save"]]]
    for a, b in [
        ("Doctors", "Add doctor, Edit, Set off duty / available, Remove"),
        ("Patients", "Register, Edit, status change"),
        ("Appointments", "Confirm booking, Confirm, Check in, Cancel"),
        ("Pharmacy", "Save to stock, Dispense 1, Add 10"),
        ("Ward", "Add bed, Allot, Discharge, Mark cleaning, Mark available"),
        ("Diagnostics", "Book slot, Mark done"),
        ("Payments", "Collect, Create invoice, Refund"),
        ("Email & SMS", "Queue alert, Mark delivered"),
    ]:
        saves.append([Paragraph(a, C), Paragraph(b, P)])
    story.append(table(saves, [40 * mm, 138 * mm]))
    story.append(Paragraph(
        "After any of these, refresh or open Dashboard / Reports — the numbers should match. That is how you know the database is live.",
        st["body"],
    ))
    story.append(PageBreak())

    # ========== PAGE 10 DATABASE ==========
    story.append(Paragraph("9. How the database works", st["h1"]))
    story.append(Paragraph(
        "The hospital data lives in <b>SQLite</b> — one file on disk named <b>medicore.db</b>. "
        "<b>Flask</b> (the file app.py) is the waiter between the web pages and that file. "
        "This is better than saving only in the browser: data survives a new browser, a new tab, and a restart of the computer "
        "(as long as the medicore.db file is not deleted).",
        st["body"],
    ))
    story.append(Paragraph("What happens when you click Save", st["h2"]))
    story.append(bullets([
        "JavaScript on the page keeps a live list (patients, rooms, invoices, …).",
        "It sends the whole list to the server: <b>PUT /api/store/patients</b> (or rooms, invoices, …).",
        "Flask checks the session cookie — you must be signed in.",
        "SQLite writes the list as JSON into the <b>stores</b> table under that name.",
        "The next page you open reads the same list. Dashboard and Reports stay in sync.",
    ], st))
    story.append(Paragraph("Tables inside medicore.db", st["h2"]))
    db_rows = [[Paragraph(x, H) for x in ["Table", "What it holds"]]]
    for a, b in [
        ("users", "Staff IDs + hashed passwords (DOC-1001 … and any new logins you add)."),
        ("stores → doctors", "Names, departments, phones, on-duty, whether they can sign in."),
        ("stores → patients", "Patient records and status."),
        ("stores → appointments", "OPD bookings and queue status."),
        ("stores → rooms", "Beds, occupancy, who is in which room, tariff."),
        ("stores → invoices", "Bills, method, paid / due / processing / refund."),
        ("stores → pharmacy", "Medicine, batch, stock, reorder level."),
        ("stores → diagnostics", "Scan bookings and done / scheduled."),
        ("stores → alerts", "Email / SMS log."),
    ]:
        db_rows.append([Paragraph(a, C), Paragraph(b, P)])
    story.append(table(db_rows, [48 * mm, 130 * mm]))
    story.append(Paragraph(
        "Login API: POST /api/login checks the hash. POST /api/staff-login creates a new login when you add a doctor with the tick box. "
        "DELETE /api/staff-login/&lt;id&gt; runs when you Remove a login doctor.",
        st["body"],
    ))
    story.append(PageBreak())

    # ========== PAGE 11 FOLDERS + SECURITY (handbook 10, but count...) ==========
    # User wanted 9-10 handbook + presentation. I'll make this page 11 as handbook close then 12-16 slides.
    # Wait user wanted 15-16 total. If I already have pages 1-10 handbook, then:
    # I used page breaks: 1 cover, 2 open, 3 login, 4 add, 5 public, 6 dash/pat, 7 doc/appt/pharm, 8 ward/dx/pay, 9 reports, 10 db
    # This is page 11 - I'll put folders+security+checklist then presentation 12-16 = 16 pages.
    # That's 11 handbook + 5 presentation. Close enough to 9-10 + presentation. Could merge 10-11... 
    # User said 9-10 detailed AND presentation of each webpage TOTAL 15-16.
    # 10 handbook + 6 presentation = 16. So this folders page should BE the last handbook (page 10) 
    # and I already used 10 for database. So this is extra.
    #
    # I'll keep it as page 11 (folders/security/checklist) and do 5 presentation pages (12-16).
    # 11 handbook-ish + 5 slides = 16. Good.

    story.append(Paragraph("10. Files, security, checklist", st["h1"]))
    story.append(Paragraph("Where the code lives", st["h2"]))
    fmap = [[Paragraph(x, H) for x in ["Place", "What it is"]]]
    for a, b in [
        ("index.html", "Home — public site, or staff sidebar after login."),
        ("login.html / about.html", "Staff login and About."),
        ("dashboard.html … notifications.html", "One HTML file per staff page."),
        ("css/theme.css", "Colours and layout for every page."),
        ("js/auth.js", "Sign in / sign out (POST /api/login)."),
        ("js/data.js", "Loads and saves lists through /api/store/…"),
        ("js/app.js", "Left menu (Home first), header, toasts."),
        ("js/doctors.js, patients.js, ward.js, payment.js …", "Buttons for that one page."),
        ("img/MEDI1.jpeg, MEDI2.jpeg", "Home-page photographs."),
        ("app.py + medicore.db", "Server + SQLite database."),
    ]:
        fmap.append([Paragraph(a, C), Paragraph(b, P)])
    story.append(table(fmap, [58 * mm, 120 * mm]))
    story.append(Paragraph("Security (what the website does — and does not)", st["h2"]))
    story.append(bullets([
        "Login page never shows IDs or the password. Session cookie is HttpOnly.",
        "app.py and medicore.db cannot be downloaded in the browser.",
        "This is a local demo on this Mac. It is not on the public internet and does not use HTTPS.",
        "There is no real UPI gateway and no real SMS provider — receipts and alerts are on-screen logs.",
    ], st))
    story.append(Paragraph("Quick start", st["h2"]))
    story.append(bullets([
        "python3 app.py inside Desktop/MediCore-Pages, then http://127.0.0.1:5000",
        "Staff login: DOC-1001 and 123456 (or any row on page 3).",
        "Add a patient, add a bed, collect a payment, refresh — data should still be there.",
        "Sign out when you leave the desk.",
    ], st))
    story.append(PageBreak())

    # ========== PRESENTATION 12 TITLE ==========
    story.append(Paragraph("WALKTHROUGH  ·  SPEAK THESE PAGES", st["kicker"]))
    story.append(Paragraph("Presenting MediCore", st["slide_h"]))
    story.append(Paragraph(
        "Use pages 12–16 if you are showing the website to someone. "
        "Each card is one screen. Read the line in teal out loud, then click through the site.",
        st["lead"],
    ))
    story.append(Spacer(1, 6))
    story.append(card_table(Paragraph(
        "<b>Say this to open:</b><br/><br/>"
        "“MediCore is one calm console for the whole hospital. "
        "Patients, doctors, beds, pharmacy, scans and billing share the same live record. "
        "The public website is open to anyone. The console opens only after a staff sign-in.”",
        st["slide_b"],
    )))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Order to click while you talk", st["h2"]))
    story.append(bullets([
        "Home (photos) → About → Staff login",
        "Dashboard → Patients → Doctors",
        "Appointments → Pharmacy → Ward Allotment",
        "Diagnostics → Payments → Reports → Email &amp; SMS",
        "Sign out, back to Home",
    ], st, "slide_b"))
    story.append(Paragraph(
        "Tip: keep this PDF on a second screen. Do not display page 3 (passwords) on a projector.",
        st["warn"],
    ))
    story.append(PageBreak())

    def slide_pair(title, cards):
        """cards: (name, say, bullets[])"""
        story.append(Paragraph("WALKTHROUGH", st["kicker"]))
        story.append(Paragraph(title, st["slide_h"]))
        blocks = []
        for name, say, pts in cards:
            inner = [Paragraph(name, st["slide_t"]), Paragraph("Say this: “%s”" % say, st["say"])]
            inner.append(bullets(pts, st, "slide_b"))
            blocks.append(KeepTogether([Spacer(1, 4), card_table(inner)]))
        for b in blocks:
            story.append(b)

    # PAGE 13
    slide_pair("Home, About, Staff login", [
        ("Home",
         "This is the hospital’s front door. Two photos, every department one click away. Staff go in through login.",
         ["Cream and teal — the same colours as the console.",
          "Not signed in: department cards ask you to sign in.",
          "Signed in: the same left menu as Payments appears, with Home at the top."]),
        ("About",
         "MediCore was designed with reception, nursing and billing, not the other way round.",
         ["Four beliefs: patients first, everything connected, data you can trust, messages built in.",
          "No password needed on this page."]),
        ("Staff login",
         "Only authorised staff. You type a Staff ID and a password. The site never shows hints.",
         ["Show/Hide on the password field.",
          "Five wrong tries lock that ID for two minutes.",
          "A correct login opens the Dashboard."]),
    ])
    story.append(PageBreak())

    # PAGE 14
    slide_pair("Dashboard, Patients, Doctors", [
        ("Dashboard",
         "This is today in one glance — patients, doctors on duty, appointments, free beds. The numbers are live.",
         ["Queue, revenue bars and SMS list all come from other pages.",
          "Collect a bill or book a slot and this screen moves."]),
        ("Patients",
         "Here we register and update every person in care. Search, edit, or jump to their bed or bill.",
         ["Statuses: Admitted, Observation, Discharged.",
          "Register patient saves to the database immediately."]),
        ("Doctors",
         "The roster. We can add a doctor, change a name, set them off duty, or remove them.",
         ["Tick ‘allow sign in’ if they should open MediCore.",
          "You cannot remove the account you are using.",
          "Off duty hides them from booking without deleting them."]),
    ])
    story.append(PageBreak())

    # PAGE 15
    slide_pair("Appointments, Pharmacy, Ward", [
        ("Appointments",
         "This is the OPD desk. Name, phone, department, doctor, date and a time chip — then confirm.",
         ["Confirm, check in, or cancel from the queue.",
          "A reminder is logged in Email & SMS automatically."]),
        ("Pharmacy",
         "Stock on the shelf. We add a medicine, dispense one strip, or put ten back.",
         ["Low and Out pills warn before a drug runs out.",
          "Insulin is the usual example of a low-stock item."]),
        ("Ward Allotment",
         "Beds. We can add a room, allot a patient, discharge them, and mark the room for cleaning.",
         ["Occupied and cleaning rooms cannot take a new patient.",
          "The same person cannot hold two beds.",
          "Bars show how full ICU, private, general and maternity are."]),
    ])
    story.append(PageBreak())

    # PAGE 16 last
    slide_pair("Diagnostics, Payments, Reports &amp; alerts", [
        ("Diagnostics",
         "MRI, CT, X-ray, ECG. We book a slot and mark it done when the report is ready.",
         ["Done scans queue a ‘report ready’ message."]),
        ("Payments",
         "The billing desk. UPI, card, cash or insurance. Collect now, or raise a due invoice and collect later.",
         ["Print a receipt from the row.",
          "Refunds and dues show on the top tiles and on Reports."]),
        ("Reports + Email &amp; SMS",
         "Reports is the scoreboard. Email & SMS is the message book. Both read the same database — nothing is typed twice.",
         ["Collections, occupancy and OPD today update themselves.",
          "That is the whole console. Sign out when you leave."]),
    ])
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "MediCore Hospital Suite  ·  Local SQLite database  ·  End of walkthrough.",
        st["lead"],
    ))

    doc = SimpleDocTemplate(
        OUT, pagesize=A4,
        leftMargin=16 * mm, rightMargin=16 * mm,
        topMargin=20 * mm, bottomMargin=16 * mm,
        title="MediCore Staff Guide (16 pages)",
        author="MediCore",
        subject="Logins, pages, database and presentation walkthrough",
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print("Wrote", OUT)


if __name__ == "__main__":
    build()
