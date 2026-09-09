/* ===== PAGE JS: Appointments — book OPD, update queue ===== */
MC.ready(function () {
  if (!MC.session()) return;
  var KEY = MC.KEYS.appointments;
  var SLOTS = ["09:00 AM", "10:30 AM", "12:00 PM", "02:30 PM", "04:00 PM", "05:30 PM"];
  var slot = "10:30 AM";

  function rows() { return MC.get(KEY); }
  function fillDoctors() {
    var dept = document.getElementById("cDept").value;
    var docs = MC.get(MC.KEYS.doctors).filter(function (d) { return d.available && (!dept || d.department === dept); });
    if (!docs.length) docs = MC.get(MC.KEYS.doctors).filter(function (d) { return d.available; });
    document.getElementById("cDoctor").innerHTML = docs.map(function (d) {
      return '<option value="' + d.id + '">' + MC.esc(d.name) + " — " + MC.esc(d.department) + "</option>";
    }).join("");
  }

  function render() {
    var q = (document.getElementById("search").value || "").toLowerCase();
    var st = document.getElementById("fStatus").value;
    var list = rows().filter(function (a) {
      var blob = (a.id + " " + a.patient + " " + MC.doctorName(a.doctorId)).toLowerCase();
      if (q && blob.indexOf(q) === -1) return false;
      if (st && a.status !== st) return false;
      return true;
    });
    var today = rows().filter(function (a) { return a.date === MC.today(); });
    document.getElementById("kpis").innerHTML =
      kpi("Today", today.length, "slots") +
      kpi("Confirmed", rows().filter(function (a) { return a.status === "Confirmed"; }).length, "ready") +
      kpi("Checked-in", rows().filter(function (a) { return a.status === "Checked-in"; }).length, "in clinic") +
      kpi("Pending", rows().filter(function (a) { return a.status === "Pending"; }).length, "awaiting");

    document.getElementById("tbody").innerHTML = list.map(function (a) {
      return "<tr><td class='mono'>" + MC.esc(a.id) + "</td><td>" + MC.esc(a.patient) + "</td><td>" + MC.esc(MC.doctorName(a.doctorId)) +
        "</td><td>" + MC.fmtDate(a.date) + "</td><td>" + MC.esc(a.time) + "</td><td>" + MC.pill(a.status) +
        "</td><td class='row-actions'>" +
        (a.status === "Pending" ? "<button class='btn btn-primary btn-sm' data-st='Confirmed' data-id='" + a.id + "'>Confirm</button>" : "") +
        (a.status === "Confirmed" ? "<button class='btn btn-primary btn-sm' data-st='Checked-in' data-id='" + a.id + "'>Check in</button>" : "") +
        (a.status !== "Cancelled" && a.status !== "Checked-in" ? "<button class='btn btn-danger btn-sm' data-st='Cancelled' data-id='" + a.id + "'>Cancel</button>" : "") +
        "</td></tr>";
    }).join("") || '<tr><td colspan="7" class="empty">No appointments.</td></tr>';
    document.getElementById("mobileList").innerHTML = list.map(function (a) {
      return '<article class="m-card"><div class="top"><strong>' + MC.esc(a.patient) + "</strong>" + MC.pill(a.status) +
        "</div><div>" + MC.esc(MC.doctorName(a.doctorId)) + " · " + MC.esc(a.time) + "</div></article>";
    }).join("");
    if (window.MCApplyI18n) MCApplyI18n();
  }
  function kpi(l, v, m) {
    return '<article class="kpi"><div class="kpi-label">' + l + '</div><div class="kpi-value">' + v + '</div><div class="kpi-meta">' + m + "</div></article>";
  }

  document.getElementById("cDate").value = MC.today();
  fillDoctors();
  document.getElementById("cDept").addEventListener("change", fillDoctors);
  document.getElementById("slots").innerHTML = SLOTS.map(function (s) {
    return '<button type="button" class="chip' + (s === slot ? " on" : "") + '" data-slot="' + s + '">' + s + "</button>";
  }).join("");
  document.getElementById("slots").addEventListener("click", function (e) {
    var s = e.target.getAttribute("data-slot");
    if (!s) return;
    slot = s;
    document.querySelectorAll("#slots .chip").forEach(function (b) { b.classList.toggle("on", b.getAttribute("data-slot") === slot); });
  });

  document.getElementById("bookForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var name = document.getElementById("cName").value.trim();
    var phone = document.getElementById("cPhone").value.trim();
    document.getElementById("f-name").classList.toggle("invalid", !name);
    document.getElementById("f-phone").classList.toggle("invalid", !phone);
    if (!name || !phone) return;
    var all = rows();
    var match = MC.get(MC.KEYS.patients).filter(function (p) {
      return String(p.name || "").toLowerCase() === name.toLowerCase();
    })[0];
    var row = {
      id: MC.nextId(all, "AP-", 5512),
      patient: name,
      patientId: match ? match.id : "",
      phone: phone,
      doctorId: document.getElementById("cDoctor").value,
      department: document.getElementById("cDept").value,
      date: document.getElementById("cDate").value || MC.today(),
      time: slot,
      status: "Confirmed"
    };
    all.unshift(row);
    MC.set(KEY, all);
    MC.logAlert(phone, "Appointment Reminder", "Queued");
    MC.toast("Booked " + row.id + " at " + slot);
    e.target.reset();
    document.getElementById("cDate").value = MC.today();
    fillDoctors();
    render();
  });

  document.body.addEventListener("click", function (e) {
    var id = e.target.getAttribute("data-id");
    var st = e.target.getAttribute("data-st");
    if (!id || !st) return;
    MC.set(KEY, rows().map(function (a) { if (a.id === id) a.status = st; return a; }));
    MC.toast(id + " → " + st);
    render();
  });
  ["search", "fStatus"].forEach(function (id) {
    document.getElementById(id).addEventListener("input", render);
    document.getElementById(id).addEventListener("change", render);
  });
  render();
});
