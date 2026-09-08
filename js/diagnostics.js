/* ===== PAGE JS: Diagnostics — MRI / CT / X-ray slots ===== */
MC.ready(function () {
  if (!MC.session()) return;
  var KEY = MC.KEYS.diagnostics;
  function rows() { return MC.get(KEY); }
  function render() {
    var q = (document.getElementById("search").value || "").toLowerCase();
    var st = document.getElementById("fStatus").value;
    var list = rows().filter(function (r) {
      if (q && (r.patient + " " + r.test).toLowerCase().indexOf(q) === -1) return false;
      if (st && r.status !== st) return false;
      return true;
    });
    document.getElementById("kpis").innerHTML =
      kpi("Today", rows().filter(function (r) { return r.date === MC.today(); }).length, "scans") +
      kpi("Scheduled", rows().filter(function (r) { return r.status === "Scheduled"; }).length, "waiting") +
      kpi("Done", rows().filter(function (r) { return r.status === "Done"; }).length, "reported") +
      kpi("MRI", rows().filter(function (r) { return r.test.indexOf("MRI") !== -1; }).length, "slots");
    document.getElementById("tbody").innerHTML = list.map(function (r) {
      return "<tr><td class='mono'>" + MC.esc(r.id) + "</td><td>" + MC.esc(r.patient) + "</td><td>" + MC.esc(r.test) +
        "</td><td>" + MC.fmtDate(r.date) + "</td><td>" + MC.esc(r.slot) + "</td><td>" + MC.pill(r.status) +
        "</td><td class='row-actions'>" + dxButtons(r) + "</td></tr>";
    }).join("") || '<tr><td colspan="7" class="empty">No scans.</td></tr>';
    document.getElementById("mobileList").innerHTML = list.map(function (r) {
      return '<article class="m-card"><div class="top"><strong>' + MC.esc(r.patient) + "</strong>" + MC.pill(r.status) +
        "</div><div>" + MC.esc(r.test) + " · " + MC.esc(r.slot) + "</div><div class='row-actions' style='margin-top:8px'>" +
        dxButtons(r) + "</div></article>";
    }).join("");
    if (window.MCApplyI18n) MCApplyI18n();
  }
  function dxButtons(r) {
    var st = r.status;
    var bits = [];
    if (st !== "Done") bits.push("<button class='btn btn-primary btn-sm' data-id='" + r.id + "' data-st='Done'>Mark done</button>");
    if (st === "Done") bits.push("<button class='btn btn-ghost btn-sm' data-mail='" + r.id + "'>Log report mail</button>");
    if (st === "Done" || st === "Cancelled") bits.push("<button class='btn btn-ghost btn-sm' data-id='" + r.id + "' data-st='Scheduled'>Undo / re-schedule</button>");
    if (st !== "Cancelled") bits.push("<button class='btn btn-danger btn-sm' data-id='" + r.id + "' data-st='Cancelled'>Cancel</button>");
    return bits.join(" ");
  }
  function kpi(l, v, m) {
    return '<article class="kpi"><div class="kpi-label">' + l + '</div><div class="kpi-value">' + v + '</div><div class="kpi-meta">' + m + "</div></article>";
  }
  document.getElementById("cDate").value = MC.today();
  var names = MC.get(MC.KEYS.patients).map(function (p) { return p.name; });
  document.getElementById("pList").innerHTML = names.map(function (n) { return '<option value="' + MC.esc(n) + '">'; }).join("");
  document.getElementById("addForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var patient = document.getElementById("cPatient").value.trim();
    if (!patient) return;
    var all = rows();
    var match = MC.get(MC.KEYS.patients).filter(function (p) {
      return String(p.name || "").toLowerCase() === patient.toLowerCase();
    })[0];
    all.unshift({
      id: MC.nextId(all, "DX-", 2201),
      patient: patient,
      patientId: match ? match.id : "",
      test: document.getElementById("cTest").value,
      slot: document.getElementById("cSlot").value,
      date: document.getElementById("cDate").value || MC.today(),
      status: "Scheduled"
    });
    MC.set(KEY, all);
    MC.logAlert(patient, "Scan slot booked", "Queued");
    e.target.reset();
    document.getElementById("cDate").value = MC.today();
    MC.toast("Scan scheduled");
    render();
  });
  function queueReport(id) {
    var row = rows().filter(function (r) { return r.id === id; })[0];
    MC.logAlert((row && row.patient) || "", "Email · Report ready", "Queued");
    MC.toast("Report mail queued (demo)");
  }
  document.body.addEventListener("click", function (e) {
    var mail = e.target.getAttribute("data-mail");
    if (mail) { queueReport(mail); return; }
    var id = e.target.getAttribute("data-id");
    var st = e.target.getAttribute("data-st");
    if (!id || !st) return;
    MC.set(KEY, rows().map(function (r) { if (r.id === id) r.status = st; return r; }));
    if (st === "Done") MC.logAlert("", "Report Ready", "Queued");
    MC.toast(id + " → " + st);
    render();
  });
  ["search", "fStatus"].forEach(function (id) {
    document.getElementById(id).addEventListener("input", render);
    document.getElementById(id).addEventListener("change", render);
  });
  render();
});
