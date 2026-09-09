/* ===== PAGE JS: Patient portal — named file, UPI / QR pay ===== */
MC.ready(function () {
  if (!MC.requirePatient()) return;
  var home = MC._patientHome || {};
  var me = MC.session();
  var payCfg = { vpa: "medicore@upi", payee: "MediCore Hospital" };
  var payTab = "upi";

  document.getElementById("signOutBtn").addEventListener("click", function () { MC.logout(); });
  var langBtn = document.getElementById("langBtn");
  if (langBtn) {
    langBtn.textContent = MC.lang() === "hi" ? "English" : "हिन्दी";
    langBtn.addEventListener("click", function () {
      MC.setLang(MC.lang() === "hi" ? "en" : "hi");
      location.reload();
    });
  }

  fetch("/api/pay/config", { credentials: "include" }).then(function (r) { return r.json(); }).then(function (c) {
    if (c && c.ok) {
      payCfg.vpa = c.vpa || payCfg.vpa;
      payCfg.payee = c.payee || payCfg.payee;
    }
  }).catch(function () {});

  function paint(pack) {
    home = pack || home;
    var p = home.patient || {};
    var doc = home.doctor || {};
    var invoices = home.invoices || [];
    var dx = home.diagnostics || [];
    var appts = home.appointments || [];
    var due = invoices.filter(function (i) { return i.status === "Due" || i.status === "Processing"; });
    var dueSum = due.reduce(function (a, i) { return a + Number(i.amount || 0); }, 0);
    var name = p.name || me.name || "patient";
    var pid = p.id || me.id;

    var fileEl = document.getElementById("filePill");
    if (fileEl) fileEl.textContent = name + " · " + pid;
    document.getElementById("whoBox").innerHTML = "<b>" + MC.esc(name) + "</b>" + MC.esc(pid);
    document.getElementById("hello").textContent = (MC.lang() === "hi" ? "नमस्ते, " : "Hello, ") + name;
    var av = document.getElementById("heroAvatar");
    if (av) av.textContent = MC.initials(name);
    var chips = document.getElementById("heroChips");
    if (chips) {
      chips.innerHTML = MC.pill(p.status || "—") +
        (p.ward ? "<span class='file-pill'>" + MC.t("Ward", "Ward") + " " + MC.esc(p.ward) + "</span>" : "") +
        "<span class='file-pill'>" + MC.esc(doc.name || p.doctorId || "") + "</span>" +
        "<span class='file-pill'>" + MC.esc(p.department || "") + "</span>";
    }

    document.getElementById("kpis").innerHTML =
      kpi(MC.t("Patient ID", "Patient ID"), pid, MC.t("keep this to sign in", "keep this to sign in")) +
      kpi(MC.t("Open bills", "Open bills"), MC.inr(dueSum), due.length + " " + MC.t("to pay", "to pay")) +
      kpi(MC.t("Reports", "Reports"), dx.length, dx.filter(function (d) { return d.status === "Done"; }).length + " " + MC.t("ready", "ready")) +
      kpi(MC.t("Appointments", "Appointments"), appts.length, MC.t("on your file", "on your file"));

    document.getElementById("details").innerHTML =
      row(MC.t("Full name", "Full name"), p.name) +
      row(MC.t("Patient ID", "Patient ID"), p.id) +
      row(MC.t("Age / gender", "Age / gender"), (p.age || "—") + " / " + (p.gender || "—")) +
      row(MC.t("Phone", "Phone"), p.phone) +
      row(MC.t("Email", "Email"), p.email) +
      row(MC.t("Blood group", "Blood group"), p.blood) +
      row(MC.t("Department", "Department"), p.department) +
      row(MC.t("Doctor", "Doctor"), doc.name || p.doctorId) +
      row(MC.t("Ward", "Ward"), p.ward || "—") +
      row(MC.t("Status", "Status"), p.status);

    document.getElementById("dxBody").innerHTML = dx.length ? dx.map(function (d) {
      var print = d.status === "Done"
        ? "<button class='btn btn-ghost btn-sm' type='button' data-print='" + MC.esc(d.id) + "'>" + MC.t("Print", "Print") + "</button>"
        : "—";
      var badge = (d.status === "Done" && d.date === MC.today()) ? " <span class='file-pill'>Ready</span>" : "";
      return "<tr><td>" + MC.esc(d.test) + badge + "</td><td>" + MC.esc(d.slot) + "</td><td>" + MC.fmtDate(d.date) +
        "</td><td>" + MC.pill(d.status) + "</td><td>" + print + "</td></tr>";
    }).join("") : '<tr><td colspan="5" class="empty">' + MC.t("No reports on your file yet.", "No reports on your file yet.") + "</td></tr>";

    paintToken(appts, pid, p);
    paintReady(dx, p, doc);

    document.getElementById("billBody").innerHTML = invoices.length ? invoices.map(function (i) {
      var pay = (i.status === "Due" || i.status === "Processing")
        ? "<button class='btn btn-primary btn-sm' type='button' data-pay='" + MC.esc(i.id) + "'>" + MC.t("Pay now", "Pay now") + "</button>"
        : "—";
      return "<tr><td class='mono'>" + MC.esc(i.id) + "</td><td class='mono'>" + MC.inr(i.amount) +
        "</td><td>" + MC.pill(i.status) + "</td><td>" + pay + "</td></tr>";
    }).join("") : '<tr><td colspan="4" class="empty">' + MC.t("No bills on your file.", "No bills on your file.") + "</td></tr>";

    document.getElementById("apBody").innerHTML = appts.length ? appts.map(function (a) {
      return "<tr><td>" + MC.fmtDate(a.date) + " · " + MC.esc(a.time) + "</td><td>" + MC.esc(a.department) +
        "</td><td>" + MC.pill(a.status) + "</td></tr>";
    }).join("") : '<tr><td colspan="3" class="empty">' + MC.t("No appointments booked.", "No appointments booked.") + "</td></tr>";

    if (window.MCApplyI18n) MCApplyI18n();
  }

  function kpi(l, v, m) {
    return '<article class="kpi"><div class="kpi-label">' + l + '</div><div class="kpi-value">' + v + '</div><div class="kpi-meta">' + m + "</div></article>";
  }
  function row(l, v) {
    return '<div class="dl-row"><span>' + MC.esc(l) + "</span><b>" + MC.esc(v == null || v === "" ? "—" : v) + "</b></div>";
  }

  function slotMins(t) {
    var m = String(t || "").match(/(\d+):(\d+)\s*(AM|PM)/i);
    if (!m) return 0;
    var h = parseInt(m[1], 10) % 12;
    if (/pm/i.test(m[3])) h += 12;
    return h * 60 + parseInt(m[2], 10);
  }

  function paintToken(appts, pid, p) {
    var card = document.getElementById("tokenCard");
    if (!card) return;
    var today = MC.today();
    var mine = (appts || []).filter(function (a) {
      return a.date === today && a.status !== "Cancelled" &&
        (a.patientId === pid || String(a.patient || "").toLowerCase() === String(p.name || "").toLowerCase());
    })[0];
    if (!mine) { card.hidden = true; return; }
    if (mine.status === "Checked-in") {
      card.hidden = false;
      card.innerHTML = "<b>" + MC.t("At the desk", "At the desk") + "</b><span>" + MC.esc(mine.time) + " · " + MC.esc(mine.department) + "</span>";
      return;
    }
    var queue = (appts || []).filter(function (a) {
      return a.date === today && a.status !== "Cancelled";
    }).sort(function (a, b) { return slotMins(a.time) - slotMins(b.time); });
    var idx = -1;
    queue.forEach(function (a, i) {
      if (a.id === mine.id) idx = i;
    });
    var pos = idx + 1;
    var wait = Math.max(0, idx) * 15;
    card.hidden = false;
    card.innerHTML = "<b>" + MC.t("You are", "You are") + " " + pos + (pos === 1 ? "st" : pos === 2 ? "nd" : pos === 3 ? "rd" : "th") + "</b><span>" +
      (wait ? MC.t("about", "about") + " " + wait + " " + MC.t("min", "min") : MC.t("next in", "next in")) +
      " · " + MC.esc(mine.time) + "</span>";
  }

  function paintReady(dx, p, doc) {
    var ban = document.getElementById("readyBanner");
    if (!ban) return;
    var ready = (dx || []).filter(function (d) { return d.status === "Done" && d.date === MC.today(); });
    if (!ready.length) { ban.hidden = true; return; }
    var d = ready[0];
    ban.hidden = false;
    ban.innerHTML = "<span>" + MC.t("Your report is ready", "Your report is ready") + ": <b>" + MC.esc(d.test) + "</b></span>" +
      "<button class='btn btn-primary btn-sm' type='button' data-print='" + MC.esc(d.id) + "'>" + MC.t("Print", "Print") + "</button>";
  }

  function letterhead(title, body) {
    return '<div class="receipt-pro">' +
      '<div class="r-head"><img src="img/logo-LIVE.jpg" alt="MediCore" width="52" height="52" />' +
      "<div><h4>MediCore Hospital</h4><p>Sion–Bandra Link Road, Mumbai 400022<br>Emergency 022 2416 2400 · Ambulance 108</p></div></div>" +
      "<h3 style='margin:12px 0 10px;color:#0B2E2B'>" + title + "</h3>" + body +
      "<p class='r-foot'>This is a computer-generated document. No signature is required.</p></div>";
  }

  function printSheet(html) {
    var el = document.getElementById("printSheet");
    el.innerHTML = html;
    window.print();
  }

  function printReport(id) {
    var p = (home.patient || {});
    var doc = (home.doctor || {});
    var d = (home.diagnostics || []).filter(function (x) { return x.id === id; })[0];
    if (!d || d.status !== "Done") { MC.toast(MC.t("Report is not ready", "Report is not ready"), "bad"); return; }
    printSheet(letterhead("Diagnostic report",
      '<div class="r-row"><span>Patient</span><strong>' + MC.esc(p.name || "") + " · " + MC.esc(p.id || "") + "</strong></div>" +
      '<div class="r-row"><span>Department</span><span>' + MC.esc(p.department || "") + "</span></div>" +
      '<div class="r-row"><span>Doctor</span><span>' + MC.esc(doc.name || p.doctorId || "") + "</span></div>" +
      '<div class="r-row"><span>Test</span><strong>' + MC.esc(d.test) + "</strong></div>" +
      '<div class="r-row"><span>Slot</span><span>' + MC.esc(d.slot || "—") + "</span></div>" +
      '<div class="r-row"><span>Date</span><span>' + MC.fmtDate(d.date) + "</span></div>" +
      '<div class="r-row"><span>Status</span><span>' + MC.esc(d.status) + "</span></div>" +
      '<div class="r-row"><span>Report ID</span><span class="mono">' + MC.esc(d.id) + "</span></div>"
    ));
  }

  function printPass() {
    var p = home.patient || {};
    printSheet(letterhead("Visitor pass",
      '<div class="r-row"><span>Patient</span><strong>' + MC.esc(p.name || "") + "</strong></div>" +
      '<div class="r-row"><span>Patient ID</span><span>' + MC.esc(p.id || "") + "</span></div>" +
      '<div class="r-row"><span>Ward</span><strong>' + MC.esc(p.ward || "Ask reception") + "</strong></div>" +
      '<div class="r-row"><span>Department</span><span>' + MC.esc(p.department || "") + "</span></div>" +
      '<div class="r-row"><span>Date</span><span>' + MC.fmtDate(MC.today()) + "</span></div>" +
      '<div class="r-row r-total"><span>Visiting hours</span><span>4:00 PM – 7:00 PM</span></div>' +
      "<p class='hint' style='margin-top:12px'>Show this at the gate. One attendant with the patient on the ward.</p>"
    ));
  }

  function upiLink(inv) {
    return "upi://pay?pa=" + encodeURIComponent(payCfg.vpa) +
      "&pn=" + encodeURIComponent(payCfg.payee) +
      "&am=" + encodeURIComponent(Number(inv.amount || 0).toFixed(2)) +
      "&cu=INR&tn=" + encodeURIComponent(inv.id);
  }

  function showTab(id) {
    payTab = id;
    document.querySelectorAll(".pay-tabs button").forEach(function (b) {
      b.classList.toggle("on", b.getAttribute("data-tab") === id);
    });
    document.getElementById("paneUpi").style.display = id === "upi" ? "block" : "none";
    document.getElementById("paneQr").style.display = id === "qr" ? "block" : "none";
    document.getElementById("paneCard").style.display = id === "card" ? "block" : "none";
  }

  document.body.addEventListener("click", function (e) {
    var tab = e.target.getAttribute("data-tab");
    if (tab) { showTab(tab); return; }
    var copy = e.target.id === "copyUpi";
    if (copy) {
      var href = document.getElementById("upiHref").textContent;
      if (navigator.clipboard) navigator.clipboard.writeText(href);
      MC.toast(MC.t("Copy UPI link", "Copy UPI link"));
      return;
    }
    if (e.target.id === "passBtn") { printPass(); return; }
    var pr = e.target.getAttribute("data-print");
    if (pr) { printReport(pr); return; }
    var id = e.target.getAttribute("data-pay");
    if (!id) return;
    var inv = (home.invoices || []).filter(function (x) { return x.id === id; })[0];
    if (!inv) return;
    document.getElementById("payId").value = id;
    document.getElementById("paySub").textContent = id + " · " + MC.inr(inv.amount);
    var href = upiLink(inv);
    document.getElementById("upiHref").textContent = href;
    document.getElementById("payVpa").textContent = payCfg.vpa;
    var canvas = document.getElementById("qrCanvas");
    if (canvas && MC.drawQR) MC.drawQR(canvas, href);
    showTab("qr");
    MC.openModal("payModal");
  });

  document.getElementById("payForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var id = document.getElementById("payId").value;
    var method = payTab === "card" ? (document.getElementById("payCardKind").value || "Card") : "UPI";
    fetch("/api/patient/pay", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ invoiceId: id, method: method })
    }).then(function (r) { return r.json(); }).then(function (res) {
      if (!res.ok) { MC.toast(res.error || MC.t("Payment failed", "Payment failed"), "bad"); return; }
      MC.closeModal("payModal");
      MC.toast(MC.t("Payment recorded", "Payment recorded"));
      return fetch("/api/patient/home", { credentials: "include" }).then(function (r) { return r.json(); });
    }).then(function (pack) {
      if (pack && pack.ok) {
        MC._patientHome = pack;
        paint(pack);
      }
    }).catch(function () { MC.toast(MC.t("Cannot reach the server", "Cannot reach the server"), "bad"); });
  });

  paint(home);
});
