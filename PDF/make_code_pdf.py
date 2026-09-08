#!/usr/bin/env python3
"""MediCore code guide — needed code per webpage, visual blocks."""
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT = "/Users/mac/Desktop/MediCore-Pages/MediCore-Code-Guide.pdf"

TEAL = colors.HexColor("#0F766E")
DEEP = colors.HexColor("#0B2E2B")
SIDE = colors.HexColor("#123C38")
CREAM = colors.HexColor("#F5F2EC")
MINT = colors.HexColor("#CCFBF1")
LINE = colors.HexColor("#E4DDD2")
TEXT = colors.HexColor("#134E4A")
MUTED = colors.HexColor("#5C6B68")
WHITE = colors.white
CODE_FG = colors.HexColor("#E7F5F3")
CODE_DIM = colors.HexColor("#9FCCC6")


def S():
    b = getSampleStyleSheet()
    return {
        "kicker": ParagraphStyle("k", parent=b["Normal"], fontName="Helvetica-Bold",
                                 fontSize=9, textColor=TEAL, spaceAfter=4, leading=12),
        "h1": ParagraphStyle("h1", parent=b["Heading1"], fontName="Helvetica-Bold",
                             fontSize=18, textColor=colors.HexColor("#0B2E2B"),
                             spaceAfter=6, leading=22),
        "h2": ParagraphStyle("h2", parent=b["Heading2"], fontName="Helvetica-Bold",
                             fontSize=11.5, textColor=TEAL, spaceBefore=6, spaceAfter=4, leading=14),
        "body": ParagraphStyle("body", parent=b["BodyText"], fontName="Helvetica",
                               fontSize=9.5, textColor=TEXT, leading=13.2, spaceAfter=5),
        "lead": ParagraphStyle("lead", parent=b["Normal"], fontName="Helvetica",
                               fontSize=10.5, textColor=MUTED, leading=15, spaceAfter=8),
        "file": ParagraphStyle("file", parent=b["Normal"], fontName="Helvetica-Bold",
                               fontSize=8, textColor=MINT, leading=11, spaceAfter=2),
        "code": ParagraphStyle("code", parent=b["Normal"], fontName="Courier",
                               fontSize=7.4, textColor=CODE_FG, leading=10.2, spaceAfter=0),
        "why": ParagraphStyle("why", parent=b["Normal"], fontName="Helvetica-Oblique",
                              fontSize=9, textColor=TEAL, leading=12.5, spaceAfter=4),
        "th": ParagraphStyle("th", parent=b["Normal"], fontName="Helvetica-Bold",
                             fontSize=8, textColor=WHITE, leading=11),
        "td": ParagraphStyle("td", parent=b["Normal"], fontName="Helvetica",
                             fontSize=8.5, textColor=TEXT, leading=12),
        "tdc": ParagraphStyle("tdc", parent=b["Normal"], fontName="Helvetica-Bold",
                              fontSize=8.5, textColor=colors.HexColor("#0B2E2B"), leading=12),
    }


def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(SIDE)
    canvas.rect(0, h - 13 * mm, w, 13 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(16 * mm, h - 8 * mm, "MediCore  ·  How each page works (code)")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w - 16 * mm, h - 8 * mm, "Internal use")
    canvas.setFillColor(TEAL)
    canvas.rect(0, 0, w, 11 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(16 * mm, 4.5 * mm, "Excerpts only — full files live in Desktop/MediCore-Pages")
    canvas.drawRightString(w - 16 * mm, 4.5 * mm, "Page %d of 16" % doc.page)
    canvas.restoreState()


def code_block(label, text, st, width=178 * mm):
    html = escape(text).replace("\n", "<br/>").replace("  ", "&nbsp;&nbsp;")
    inner = [
        [Paragraph(label, st["file"])],
        [Paragraph(html, st["code"])],
    ]
    t = Table(inner, colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DEEP),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (0, 0), 7),
        ("BOTTOMPADDING", (0, 0), (0, 0), 2),
        ("TOPPADDING", (0, 1), (0, 1), 2),
        ("BOTTOMPADDING", (0, 1), (0, 1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 0.5, TEAL),
    ]))
    return t


def grid(rows, widths):
    t = Table(rows, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, CREAM]),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def build():
    st = S()
    H, P, C = st["th"], st["td"], st["tdc"]
    story = []

    # 1 cover
    story.append(Paragraph("CODE WALKTHROUGH  ·  16 PAGES", st["kicker"]))
    story.append(Paragraph("How each webpage works", st["h1"]))
    story.append(Paragraph(
        "This book shows only the code that makes a page save, log in, or update the screen. "
        "It is not a dump of every file. Pair it with MediCore-Staff-Guide.pdf for logins and simple words.",
        st["lead"],
    ))
    story.append(Paragraph("The same 3 layers on every staff page", st["h2"]))
    rows = [[Paragraph(x, H) for x in ["Layer", "Files", "Job"]]]
    rows += [
        [Paragraph("1. HTML", C), Paragraph("patients.html, payment.html, …", P),
         Paragraph("Boxes on screen: forms, table ids, buttons.", P)],
        [Paragraph("2. Page JS", C), Paragraph("js/patients.js, js/ward.js, …", P),
         Paragraph("What happens on click. Calls MC.set to save.", P)],
        [Paragraph("3. Shared JS", C), Paragraph("js/data.js, auth.js, app.js", P),
         Paragraph("Login, left menu, talk to SQLite.", P)],
        [Paragraph("4. Server", C), Paragraph("app.py + medicore.db", P),
         Paragraph("Checks the session and writes the database.", P)],
    ]
    story.append(grid(rows, [28 * mm, 58 * mm, 92 * mm]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Scripts at the bottom of a staff page (always this order)", st["h2"]))
    story.append(code_block("example: payment.html (end of file)",
"""<script src="js/data.js"></script>
<script src="js/auth.js"></script>
<script src="js/app.js"></script>
<script src="js/payment.js"></script>""", st))
    story.append(Paragraph(
        "data.js loads first so MC.get / MC.set exist. auth.js adds login. app.js draws the teal menu. "
        "Then the page file (payment.js) wires the buttons.",
        st["body"],
    ))
    story.append(PageBreak())

    # 2 data.js
    story.append(Paragraph("SHARED — saving to the database", st["kicker"]))
    story.append(Paragraph("js/data.js  ·  MC.get and MC.set", st["h1"]))
    story.append(Paragraph(
        "Every list (doctors, patients, rooms, invoices…) lives in memory (MC._cache) and on disk (medicore.db). "
        "Pages never talk to SQLite themselves. They call two functions.",
        st["body"],
    ))
    story.append(Paragraph("Why this matters: one save path for the whole hospital.", st["why"]))
    story.append(code_block("js/data.js — read a list",
"""MC.get = function (key) {
  var name = storeName(key);          // "patients", "rooms", …
  var rows = MC._cache[name];
  return Array.isArray(rows) ? rows : [];
};""", st))
    story.append(Spacer(1, 6))
    story.append(code_block("js/data.js — save a list (screen + database)",
"""MC.set = function (key, rows) {
  var name = storeName(key);
  MC._cache[name] = rows;             // 1. update the screen cache
  fetch("/api/store/" + name, {       // 2. send the full list to Flask
    method: "PUT",
    credentials: "include",           // session cookie = who is signed in
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(rows)
  });
  return rows;
};""", st))
    story.append(Paragraph(
        "Flask receives PUT /api/store/patients, checks you are logged in, then writes JSON into SQLite. "
        "Dashboard and Reports call MC.get on the same keys, so their numbers match.",
        st["body"],
    ))
    story.append(code_block("js/data.js — new IDs (PT-4407, INV-77125, …)",
"""MC.nextId = function (rows, prefix, start) {
  var nums = rows.map(function (x) {
    return parseInt(String(x.id).replace(/\\D/g, ""), 10);
  });
  var n = Math.max.apply(null, nums) + 1;
  return prefix + n;   // e.g. prefix "PT-" → "PT-4407"
};""", st))
    story.append(PageBreak())

    # 3 auth + shell
    story.append(Paragraph("SHARED — login and the teal menu", st["kicker"]))
    story.append(Paragraph("js/auth.js + js/app.js", st["h1"]))
    story.append(Paragraph(
        "Passwords never sit in the HTML. The browser posts Staff ID + password to Flask. "
        "A cookie is stored. Later saves send that cookie automatically (credentials: include).",
        st["body"],
    ))
    story.append(code_block("js/auth.js — sign in",
"""MC.login = function (id, password) {
  return fetch("/api/login", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id: id, password: password })
  }).then(function (r) { return r.json(); })
    .then(function (data) {
      if (!data.ok) return { ok: false, error: data.error };
      MC._me = data.user;             // { id, name, department }
      return { ok: true };
    });
};""", st))
    story.append(Spacer(1, 6))
    story.append(code_block("js/auth.js — block the console if not signed in",
"""MC.requireAuth = function () {
  if (MC._me) return MC._me;
  location.href = "login.html";       // kick back to login
  return null;
};""", st))
    story.append(Paragraph(
        "Staff HTML files set data-auth=\"staff\". app.js sees that, calls requireAuth, then paints the left menu from MC.NAV "
        "(Home first, then Dashboard … Email & SMS).",
        st["body"],
    ))
    story.append(code_block("every staff HTML — page title used by the header",
"""<body data-auth="staff" data-page="patients.html">
  <div id="pageTitle">Patient details</div>
  <div id="pageActions">
    <button id="openCreate">Register patient</button>
  </div>
  <aside id="sidebar"></aside>   <!-- app.js fills this -->
  <header id="topbar"></header>  <!-- title + Live + Sign out -->
  <div class="content">…forms and tables…</div>
</body>""", st))
    story.append(PageBreak())

    # 4 Home
    story.append(Paragraph("HOME  ·  index.html", st["kicker"]))
    story.append(Paragraph("Public site, or staff menu after login", st["h1"]))
    story.append(Paragraph(
        "One file, two skins. data-auth=\"home\". If there is no session, #publicRoot shows (photos, Staff login). "
        "If there is a session, #staffRoot shows — same sidebar as Payments.",
        st["body"],
    ))
    story.append(code_block("index.html — two roots",
"""<body data-auth="home" data-page="index.html">
  <div id="publicRoot">  <!-- logged out -->
    <img src="img/MEDI1.jpeg">
    <a href="login.html">Staff login</a>
    <div id="modGrid"></div>
  </div>
  <div id="staffRoot">   <!-- logged in: teal console -->
    <aside id="sidebar"></aside>
    <div id="modGridStaff"></div>
  </div>
</body>""", st))
    story.append(code_block("js/app.js — pick the skin",
"""if (auth === "home") {
  if (MC.session()) {
    publicRoot.style.display = "none";
    staffRoot.style.display = "block";
    MC.renderStaffChrome();           // same header as Payments
  } else {
    staffRoot.style.display = "none";
    publicRoot.style.display = "block";
  }
  MC.fillModuleGrid(modGrid);         // cards → login or real page
}""", st))
    story.append(Paragraph(
        "fillModuleGrid: if logged out, every department card href is login.html. If logged in, href is patients.html, ward-allotment.html, and so on.",
        st["body"],
    ))
    story.append(PageBreak())

    # 5 Login
    story.append(Paragraph("STAFF LOGIN  ·  login.html", st["kicker"]))
    story.append(Paragraph("Two fields. No hints. Talks to Flask.", st["h1"]))
    story.append(Paragraph(
        "The page never lists DOC-1001 or the password. A Show/Hide button only changes input type. "
        "On submit, bindLoginForm calls MC.login, then goes to dashboard.html.",
        st["body"],
    ))
    story.append(code_block("login.html — the only fields",
"""<form id="staffLogin">
  <label>Staff ID</label>
  <input id="loginId" autocomplete="username">
  <label>Password</label>
  <input id="loginPw" type="password" autocomplete="current-password">
  <p id="loginErr" class="error"></p>
  <button type="submit">Continue</button>
</form>""", st))
    story.append(code_block("js/app.js — submit",
"""MC.bindLoginForm = function (formId) {
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    MC.login(loginId.value, loginPw.value).then(function (res) {
      if (!res.ok) { loginErr.textContent = res.error; return; }
      location.href = "dashboard.html";
    });
  });
};""", st))
    story.append(Paragraph(
        "Flask (next pages) compares the password to a hash in the users table. Same error text for a bad ID or a bad password, so nobody can guess which one failed.",
        st["body"],
    ))
    story.append(PageBreak())

    # 6 Dashboard
    story.append(Paragraph("DASHBOARD  ·  dashboard.html + js/dashboard.js", st["kicker"]))
    story.append(Paragraph("No typing — only counting", st["h1"]))
    story.append(Paragraph(
        "The dashboard does not save. It reads lists other pages already saved, then fills four tiles and three tables.",
        st["body"],
    ))
    story.append(code_block("js/dashboard.js — tiles from live lists",
"""MC.ready(function () {
  var appts = MC.get(MC.KEYS.appointments);
  var patients = MC.get(MC.KEYS.patients);
  var rooms = MC.get(MC.KEYS.rooms);
  var invoices = MC.get(MC.KEYS.invoices);

  var onDuty = MC.get(MC.KEYS.doctors)
    .filter(function (d) { return d.available; }).length;

  var occ = rooms.reduce(function (a, r) {
    return a + Number(r.occupied || 0);
  }, 0);
  // then write HTML into #kpis, #qBody, #revBars, #smsList
});""", st))
    story.append(Paragraph(
        "MC.ready waits until /api/bootstrap has filled the cache. That is why the numbers match Patients, Ward and Payments.",
        st["body"],
    ))
    story.append(PageBreak())

    # 7 Patients
    story.append(Paragraph("PATIENTS  ·  patients.html + js/patients.js", st["kicker"]))
    story.append(Paragraph("Register and edit — then MC.set", st["h1"]))
    story.append(Paragraph("Why: one form both creates PT-4407 and updates an existing row (hidden editId).", st["why"]))
    story.append(code_block("js/patients.js — save",
"""form.addEventListener("submit", function (e) {
  e.preventDefault();
  var name = document.getElementById("cName").value.trim();
  if (!name) return;                  // show inline error
  var all = MC.get(MC.KEYS.patients);
  var eid = document.getElementById("editId").value;
  var row = {
    id: eid || MC.nextId(all, "PT-", 4401),
    name: name,
    age: Number(document.getElementById("cAge").value) || 0,
    phone: document.getElementById("cPhone").value.trim(),
    department: document.getElementById("cDept").value,
    doctorId: document.getElementById("cDoctor").value,
    status: document.getElementById("cStatus").value
  };
  if (eid) all = all.map(function (x) { return x.id === eid ? row : x; });
  else all.unshift(row);
  MC.set(MC.KEYS.patients, all);      // → PUT /api/store/patients
});""", st))
    story.append(Paragraph(
        "Search just filters the array in memory (no extra API). Ward and Bill links are normal hrefs to the other HTML files.",
        st["body"],
    ))
    story.append(PageBreak())

    # 8 Doctors
    story.append(Paragraph("DOCTORS  ·  doctors.html + js/doctors.js", st["kicker"]))
    story.append(Paragraph("Add, edit, off duty, remove, optional login", st["h1"]))
    story.append(code_block("js/doctors.js — add a doctor",
"""var newId = MC.nextId(all, "DOC-", 1007);
var canLogin = document.getElementById("cLogin").checked;
all.push({
  id: newId, name: name, department: dept,
  phone: phone, available: true, login: canLogin
});
if (canLogin) {
  fetch("/api/staff-login", {         // create hashed password on server
    method: "POST", credentials: "include",
    body: JSON.stringify({ id: newId })
  });
}
MC.set(MC.KEYS.doctors, all);""", st))
    story.append(Spacer(1, 6))
    story.append(code_block("js/doctors.js — remove (cannot remove yourself)",
"""if (del === me.id) return;            // row marked "You"
if (!confirm("Remove " + doc.name + "?")) return;
if (doc.login) {
  fetch("/api/staff-login/" + del, { method: "DELETE", credentials: "include" });
}
MC.set(KEY, rows().filter(function (d) { return d.id !== del; }));""", st))
    story.append(Paragraph(
        "Off duty only flips d.available. Appointment booking later filters available: true. "
        "Flask refuses DELETE if it is your own ID, or if you would delete the last login.",
        st["body"],
    ))
    story.append(PageBreak())

    # 9 Appointments
    story.append(Paragraph("APPOINTMENTS  ·  appointments.html + js/appointments.js", st["kicker"]))
    story.append(Paragraph("Book a slot, then change status on the queue", st["h1"]))
    story.append(code_block("js/appointments.js — confirm booking",
"""form.addEventListener("submit", function (e) {
  e.preventDefault();
  var all = MC.get(MC.KEYS.appointments);
  all.unshift({
    id: MC.nextId(all, "AP-", 5512),
    patient: name, phone: phone,
    doctorId: document.getElementById("cDoctor").value,
    department: document.getElementById("cDept").value,
    date: document.getElementById("cDate").value,
    time: slot,                       // last time-chip clicked
    status: "Confirmed"
  });
  MC.set(MC.KEYS.appointments, all);
  MC.logAlert(phone, "Appointment Reminder", "Queued");
});""", st))
    story.append(code_block("js/appointments.js — Confirm / Check in / Cancel",
"""document.body.addEventListener("click", function (e) {
  var id = e.target.getAttribute("data-id");
  var st = e.target.getAttribute("data-st");  // "Checked-in"
  if (!id || !st) return;
  MC.set(KEY, rows().map(function (a) {
    if (a.id === id) a.status = st;
    return a;
  }));
});""", st))
    story.append(Paragraph(
        "Doctor dropdown is filled from MC.get(doctors) where available is true, and filtered by department.",
        st["body"],
    ))
    story.append(PageBreak())

    # 10 Pharmacy
    story.append(Paragraph("PHARMACY  ·  pharmacy.html + js/pharmacy.js", st["kicker"]))
    story.append(Paragraph("Stock goes up and down in the same list", st["h1"]))
    story.append(code_block("js/pharmacy.js — low vs out",
"""function statusOf(r) {
  if (r.stock <= 0) return "Out";
  if (r.stock <= r.min) return "Low";   // reorder level
  return "In-stock";
}""", st))
    story.append(code_block("js/pharmacy.js — add / dispense / restock",
"""// Add medicine
all.unshift({
  id: MC.nextId(all, "RX-", 10), name: name, batch: batch,
  stock: Number(pStock.value) || 0, min: Number(pMin.value) || 10, unit: unit
});
MC.set(KEY, all);

// Dispense 1 or Add 10 (buttons data-d / data-a)
MC.set(KEY, rows().map(function (r) {
  if (r.id === d) r.stock = Math.max(0, r.stock - 1);
  if (r.id === a) r.stock += 10;
  return r;
}));""", st))
    story.append(PageBreak())

    # 11 Ward
    story.append(Paragraph("WARD ALLOTMENT  ·  ward-allotment.html + js/ward.js", st["kicker"]))
    story.append(Paragraph("Add a room, allot a patient, never double-book", st["h1"]))
    story.append(code_block("js/ward.js — add bed",
"""all.push({
  id: id.toUpperCase(),               // e.g. PR-220
  type: "Private", floor: "2nd",
  beds: beds, occupied: 0, tariff: tariff,
  occupant: "", status: "Available", patients: []
});
save(all);                            // save() → derive() then MC.set(rooms)""", st))
    story.append(code_block("js/ward.js — allot (block occupied + same patient twice)",
"""var taken = rooms.some(function (r) {
  return (r.patients || []).some(function (p) {
    return p.toLowerCase() === patient.toLowerCase();
  });
});
if (taken) return toast("already has a bed");
if (freeBeds(room) <= 0) return toast("No free bed");
room.patients.push(patient);
save(rooms);""", st))
    story.append(Paragraph(
        "derive() sets Occupied / Partially Full / Available from patients.length vs beds. "
        "Discharge pops a name; if the room is empty, status becomes Cleaning.",
        st["body"],
    ))
    story.append(PageBreak())

    # 12 Diagnostics
    story.append(Paragraph("DIAGNOSTICS  ·  diagnostics.html + js/diagnostics.js", st["kicker"]))
    story.append(Paragraph("Book a scan, mark it done", st["h1"]))
    story.append(code_block("js/diagnostics.js — book + complete",
"""all.unshift({
  id: MC.nextId(all, "DX-", 2201),
  patient: patient,
  test: document.getElementById("cTest").value,   // MRI / CT / X-Ray …
  slot: document.getElementById("cSlot").value,
  date: document.getElementById("cDate").value,
  status: "Scheduled"
});
MC.set(KEY, all);
MC.logAlert(patient, "Scan slot booked", "Queued");

// Mark done
MC.set(KEY, rows().map(function (r) {
  if (r.id === id) r.status = "Done";
  return r;
}));
MC.logAlert("", "Report Ready", "Queued");""", st))
    story.append(PageBreak())

    # 13 Payments
    story.append(Paragraph("PAYMENTS  ·  payment.html + js/payment.js", st["kicker"]))
    story.append(Paragraph("Collect, create invoice, refund, receipt", st["h1"]))
    story.append(code_block("js/payment.js — quick collect",
"""var st = (qMethod === "Insurance") ? "Processing" : "Paid";
var byId = all.filter(function (x) { return x.id === ref; })[0];
if (byId && (byId.status === "Due" || byId.status === "Processing")) {
  byId.status = st; byId.method = qMethod; byId.amount = amt;
} else {
  all.unshift({
    id: MC.nextId(all, "INV-", 77120),
    patient: ref, amount: amt, method: qMethod,
    date: MC.today(), status: st, department: "General"
  });
}
MC.set(MC.KEYS.invoices, all);
MC.logAlert(ref, "Payment receipt", "Queued");
showReceipt(id);                      // print-friendly modal""", st))
    story.append(Paragraph(
        "KPI tiles re-sum the invoice list: Paid today, Due, Insurance, Refund. "
        "Dashboard revenue bars use the same invoices grouped by department.",
        st["body"],
    ))
    story.append(PageBreak())

    # 14 Reports + SMS
    story.append(Paragraph("REPORTS + EMAIL & SMS", st["kicker"]))
    story.append(Paragraph("js/reports.js  ·  js/notifications.js", st["h1"]))
    story.append(Paragraph(
        "Reports never save. It only adds numbers from invoices, rooms and appointments. "
        "Email & SMS is a log. logAlert is used by booking, scans and payments too.",
        st["body"],
    ))
    story.append(code_block("js/reports.js — occupancy and collections",
"""var collected = invoices
  .filter(function (i) { return i.status === "Paid"; })
  .reduce(function (a, i) { return a + Number(i.amount); }, 0);
var beds = rooms.reduce(function (a, r) { return a + Number(r.beds); }, 0);
var occ  = rooms.reduce(function (a, r) { return a + Number(r.occupied); }, 0);
var pct  = beds ? Math.round(occ / beds * 100) : 0;""", st))
    story.append(code_block("js/data.js — MC.logAlert (used by many pages)",
"""MC.logAlert = function (to, template, status) {
  var rows = MC.get(MC.KEYS.alerts);
  rows.unshift({
    id: "AL-" + Date.now(),
    to: to, template: template,
    time: new Date().toTimeString().slice(0, 5),
    date: MC.today(),
    status: status || "Queued"
  });
  MC.set(MC.KEYS.alerts, rows.slice(0, 80));
};""", st))
    story.append(PageBreak())

    # 15 Flask
    story.append(Paragraph("SERVER  ·  app.py", st["kicker"]))
    story.append(Paragraph("Login check and SQLite write", st["h1"]))
    story.append(Paragraph(
        "This is the only place passwords are checked. They are stored hashed. The HTML never sees the hash.",
        st["body"],
    ))
    story.append(code_block("app.py — login (same error if ID or password is wrong)",
"""@app.post("/api/login")
def api_login():
    staff_id = request.json.get("id", "").strip().upper()
    password = request.json.get("password", "")
    row = db().execute(
        "SELECT id, password_hash FROM users WHERE id=?", (staff_id,)
    ).fetchone()
    if not row or not check_password_hash(row["password_hash"], password):
        return jsonify({"ok": False,
                        "error": "Invalid staff ID or password"}), 401
    session["uid"] = row["id"]        # HttpOnly cookie
    return jsonify({"ok": True, "user": doctor_public(row["id"])})""", st))
    story.append(code_block("app.py — save any module list",
"""@app.put("/api/store/<name>")
@login_required
def api_put_store(name):
    body = request.get_json()         # must be a JSON list
    save_store(name, body)            # UPDATE stores SET payload=… 
    return jsonify({"ok": True})""", st))
    story.append(Paragraph(
        "login_required returns 401 if the cookie is missing. Five failed logins lock that Staff ID for two minutes (_LOCK dictionary in memory).",
        st["body"],
    ))
    story.append(PageBreak())

    # 16 flow
    story.append(Paragraph("ONE CLICK, END TO END", st["kicker"]))
    story.append(Paragraph("From a button to medicore.db", st["h1"]))
    story.append(Paragraph("Example: Register patient on Patients.", st["why"]))
    flow = [[Paragraph(x, H) for x in ["Step", "Where", "What happens"]]]
    for a, b, c in [
        ("1", "patients.html", "You fill the form and press Save."),
        ("2", "js/patients.js", "Builds a row {id, name, …}. Puts it in the patients array."),
        ("3", "js/data.js MC.set", "Updates MC._cache and PUT /api/store/patients with credentials."),
        ("4", "app.py", "login_required reads the session cookie. If ok, save_store writes JSON."),
        ("5", "medicore.db", "Table stores, name='patients', payload = the full list."),
        ("6", "dashboard.js", "Next visit, MC.get(patients) counts Admitted for the tile."),
    ]:
        flow.append([Paragraph(a, C), Paragraph(b, C), Paragraph(c, P)])
    story.append(grid(flow, [16 * mm, 42 * mm, 120 * mm]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Same path on every module", st["h2"]))
    same = [[Paragraph(x, H) for x in ["Page", "Key", "Save call"]]]
    for a, b, c in [
        ("Doctors", "doctors", "MC.set(doctors) + /api/staff-login if they can sign in"),
        ("Ward", "rooms", "save(rooms) after allot / add bed / discharge"),
        ("Payments", "invoices", "MC.set(invoices) after collect / create / refund"),
        ("Appointments", "appointments", "MC.set(appointments) + MC.logAlert"),
        ("Pharmacy", "pharmacy", "MC.set(pharmacy) after stock change"),
        ("Diagnostics", "diagnostics", "MC.set(diagnostics) + MC.logAlert"),
        ("Email & SMS", "alerts", "MC.set(alerts) or MC.logAlert"),
    ]:
        same.append([Paragraph(a, C), Paragraph(b, P), Paragraph(c, P)])
    story.append(grid(same, [32 * mm, 32 * mm, 114 * mm]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Open the full files in Desktop/MediCore-Pages if you need a line the excerpt skipped. "
        "Staff logins and simple page words are in MediCore-Staff-Guide.pdf.",
        st["body"],
    ))

    doc = SimpleDocTemplate(
        OUT, pagesize=A4,
        leftMargin=16 * mm, rightMargin=16 * mm,
        topMargin=20 * mm, bottomMargin=16 * mm,
        title="MediCore Code Guide (16 pages)",
        author="MediCore",
        subject="Needed code for each webpage",
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print("Wrote", OUT)


if __name__ == "__main__":
    build()
