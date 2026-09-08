/* ===== PAGE JS: Patient portal — own file only ===== */
MC.ready(function () {
  if (!MC.requirePatient()) return;
  var home = MC._patientHome || {};
  var me = MC.session();

  document.getElementById("signOutBtn").addEventListener("click", function () { MC.logout(); });
  document.getElementById("whoBox").innerHTML = "<b>" + MC.esc(me.name) + "</b>" + MC.esc(me.id);
  document.getElementById("hello").textContent = "Hello, " + (me.name || "patient");

  function paint(pack) {
    home = pack || home;
    var p = home.patient || {};
    var doc = home.doctor || {};
    var invoices = home.invoices || [];
    var dx = home.diagnostics || [];
    var appts = home.appointments || [];
    var due = invoices.filter(function (i) { return i.status === "Due" || i.status === "Processing"; });
    var dueSum = due.reduce(function (a, i) { return a + Number(i.amount || 0); }, 0);

    document.getElementById("kpis").innerHTML =
      kpi("Patient ID", p.id || me.id, "keep this to sign in") +
      kpi("Open bills", MC.inr(dueSum), due.length + " to pay") +
      kpi("Reports", dx.length, dx.filter(function (d) { return d.status === "Done"; }).length + " ready") +
      kpi("Appointments", appts.length, "on your file");

    document.getElementById("details").innerHTML =
      row("Full name", p.name) +
      row("Patient ID", p.id) +
      row("Age / gender", (p.age || "—") + " / " + (p.gender || "—")) +
      row("Phone", p.phone) +
      row("Blood group", p.blood) +
      row("Department", p.department) +
      row("Doctor", doc.name || p.doctorId) +
      row("Ward", p.ward || "—") +
      row("Status", p.status);

    document.getElementById("dxBody").innerHTML = dx.length ? dx.map(function (d) {
      return "<tr><td>" + MC.esc(d.test) + "</td><td>" + MC.esc(d.slot) + "</td><td>" + MC.fmtDate(d.date) +
        "</td><td>" + MC.pill(d.status) + "</td></tr>";
    }).join("") : '<tr><td colspan="4" class="empty">No reports on your file yet.</td></tr>';

    document.getElementById("billBody").innerHTML = invoices.length ? invoices.map(function (i) {
      var pay = (i.status === "Due" || i.status === "Processing")
        ? "<button class='btn btn-primary btn-sm' type='button' data-pay='" + MC.esc(i.id) + "'>Pay</button>"
        : "—";
      return "<tr><td class='mono'>" + MC.esc(i.id) + "</td><td class='mono'>" + MC.inr(i.amount) +
        "</td><td>" + MC.pill(i.status) + "</td><td>" + pay + "</td></tr>";
    }).join("") : '<tr><td colspan="4" class="empty">No bills on your file.</td></tr>';

    document.getElementById("apBody").innerHTML = appts.length ? appts.map(function (a) {
      return "<tr><td>" + MC.fmtDate(a.date) + " · " + MC.esc(a.time) + "</td><td>" + MC.esc(a.department) +
        "</td><td>" + MC.pill(a.status) + "</td></tr>";
    }).join("") : '<tr><td colspan="3" class="empty">No appointments booked.</td></tr>';
  }

  function kpi(l, v, m) {
    return '<article class="kpi"><div class="kpi-label">' + l + '</div><div class="kpi-value">' + v + '</div><div class="kpi-meta">' + m + "</div></article>";
  }
  function row(l, v) {
    return '<div class="dl-row"><span>' + MC.esc(l) + "</span><b>" + MC.esc(v == null || v === "" ? "—" : v) + "</b></div>";
  }

  document.body.addEventListener("click", function (e) {
    var id = e.target.getAttribute("data-pay");
    if (!id) return;
    var inv = (home.invoices || []).filter(function (x) { return x.id === id; })[0];
    if (!inv) return;
    document.getElementById("payId").value = id;
    document.getElementById("paySub").textContent = id + " · " + MC.inr(inv.amount);
    MC.openModal("payModal");
  });

  document.getElementById("payForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var id = document.getElementById("payId").value;
    var method = document.getElementById("payMethod").value;
    fetch("/api/patient/pay", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ invoiceId: id, method: method })
    }).then(function (r) { return r.json(); }).then(function (res) {
      if (!res.ok) { MC.toast(res.error || "Payment failed", "bad"); return; }
      MC.closeModal("payModal");
      MC.toast("Payment recorded");
      return fetch("/api/patient/home", { credentials: "include" }).then(function (r) { return r.json(); });
    }).then(function (pack) {
      if (pack && pack.ok) {
        MC._patientHome = pack;
        paint(pack);
      }
    }).catch(function () { MC.toast("Cannot reach the server", "bad"); });
  });

  paint(home);
});
