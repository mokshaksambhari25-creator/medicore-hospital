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
      return "<tr><td>" + MC.esc(d.test) + "</td><td>" + MC.esc(d.slot) + "</td><td>" + MC.fmtDate(d.date) +
        "</td><td>" + MC.pill(d.status) + "</td></tr>";
    }).join("") : '<tr><td colspan="4" class="empty">' + MC.t("No reports on your file yet.", "No reports on your file yet.") + "</td></tr>";

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
