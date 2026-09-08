/* ===== PAGE JS: Admin — all patient portal files ===== */
MC.ready(function () {
  if (!MC.requireStaff()) return;
  var sess = MC.session();
  if (sess.role !== "admin") {
    location.href = "patients.html";
    return;
  }

  function matchRow(row, p) {
    return row.patientId === p.id || String(row.patient || "").toLowerCase() === String(p.name || "").toLowerCase();
  }

  function dues(p) {
    return MC.get(MC.KEYS.invoices).filter(function (i) {
      return matchRow(i, p) && (i.status === "Due" || i.status === "Processing");
    });
  }

  function reports(p) {
    return MC.get(MC.KEYS.diagnostics).filter(function (d) { return matchRow(d, p); });
  }

  function render() {
    var q = (document.getElementById("search").value || "").toLowerCase();
    var list = MC.get(MC.KEYS.patients).filter(function (p) {
      return !q || (p.id + " " + p.name + " " + p.department).toLowerCase().indexOf(q) !== -1;
    });
    document.getElementById("kpis").innerHTML =
      kpi("Patients", MC.get(MC.KEYS.patients).length, "portal logins") +
      kpi("Admitted", MC.get(MC.KEYS.patients).filter(function (p) { return p.status === "Admitted"; }).length, "in wards") +
      kpi("Open bills", MC.get(MC.KEYS.invoices).filter(function (i) { return i.status === "Due"; }).length, "due invoices") +
      kpi("Reports", MC.get(MC.KEYS.diagnostics).length, "on file");

    document.getElementById("tbody").innerHTML = list.map(function (p) {
      var d = dues(p);
      var r = reports(p);
      return "<tr><td class='mono'>" + MC.esc(p.id) + "</td><td>" + MC.esc(p.name) + "</td><td>" + MC.esc(p.department) +
        "</td><td>" + MC.pill(p.status) + "</td><td class='mono'>" + MC.inr(d.reduce(function (a, i) { return a + Number(i.amount || 0); }, 0)) +
        "</td><td class='mono'>" + r.length + "</td><td><button class='btn btn-ghost btn-sm' data-open='" + p.id + "'>Open file</button></td></tr>";
    }).join("") || '<tr><td colspan="7" class="empty">No patients.</td></tr>';

    document.getElementById("mobileList").innerHTML = list.map(function (p) {
      return '<article class="m-card"><div class="top"><strong>' + MC.esc(p.name) + "</strong>" + MC.pill(p.status) +
        "</div><div class='mono'>" + MC.esc(p.id) + "</div>" +
        "<button class='btn btn-ghost btn-sm' style='margin-top:8px' data-open='" + p.id + "'>Open file</button></article>";
    }).join("");
  }

  function kpi(l, v, m) {
    return '<article class="kpi"><div class="kpi-label">' + l + '</div><div class="kpi-value">' + v + '</div><div class="kpi-meta">' + m + "</div></article>";
  }

  function openFile(id) {
    var p = MC.get(MC.KEYS.patients).filter(function (x) { return x.id === id; })[0];
    if (!p) return;
    var card = document.getElementById("detailCard");
    card.style.display = "block";
    document.getElementById("detailTitle").textContent = p.name + " · " + p.id;
    document.getElementById("detailMeta").innerHTML =
      meta("Patient ID", p.id) + meta("Phone", p.phone) + meta("Blood", p.blood) +
      meta("Department", p.department) + meta("Doctor", MC.doctorName(p.doctorId)) +
      meta("Ward", p.ward || "—") + meta("Status", p.status);
    var dx = reports(p);
    document.getElementById("detailDx").innerHTML = dx.length ? dx.map(function (d) {
      return "<tr><td>" + MC.esc(d.test) + "</td><td>" + MC.fmtDate(d.date) + "</td><td>" + MC.pill(d.status) + "</td></tr>";
    }).join("") : '<tr><td class="empty">No reports.</td></tr>';
    var inv = MC.get(MC.KEYS.invoices).filter(function (i) { return matchRow(i, p); });
    document.getElementById("detailInv").innerHTML = inv.length ? inv.map(function (i) {
      return "<tr><td class='mono'>" + MC.esc(i.id) + "</td><td>" + MC.inr(i.amount) + "</td><td>" + MC.pill(i.status) + "</td></tr>";
    }).join("") : '<tr><td class="empty">No bills.</td></tr>';
    card.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function meta(l, v) {
    return '<div class="dl-row"><span>' + MC.esc(l) + "</span><b>" + MC.esc(v || "—") + "</b></div>";
  }

  document.getElementById("search").addEventListener("input", render);
  document.body.addEventListener("click", function (e) {
    var id = e.target.getAttribute("data-open");
    if (id) openFile(id);
  });
  render();
});
