/* ===== PAGE JS: Dashboard — live KPIs from shared stores ===== */
MC.ready(function () {
  if (!MC.session()) return;
  var appts = MC.get(MC.KEYS.appointments);
  var patients = MC.get(MC.KEYS.patients);
  var rooms = MC.get(MC.KEYS.rooms);
  var invoices = MC.get(MC.KEYS.invoices);
  var alerts = MC.get(MC.KEYS.alerts);
  var doctors = MC.get(MC.KEYS.doctors);
  var today = MC.today();

  var occ = rooms.reduce(function (a, r) { return a + (Number(r.occupied) || (r.patients || []).length); }, 0);
  var beds = rooms.reduce(function (a, r) { return a + Number(r.beds || 0); }, 0);
  var free = rooms.reduce(function (a, r) {
    if (r.status === "Cleaning") return a;
    return a + Math.max(0, r.beds - (r.occupied || 0));
  }, 0);
  var icuFree = rooms.filter(function (r) { return r.type === "ICU"; }).reduce(function (a, r) {
    return a + (r.status === "Cleaning" ? 0 : Math.max(0, r.beds - (r.occupied || 0)));
  }, 0);
  var todayAp = appts.filter(function (x) { return x.date === today; });
  var onDuty = doctors.filter(function (d) { return d.available; }).length;

  document.getElementById("kpis").innerHTML =
    tile("Active Patients", patients.filter(function (p) { return p.status !== "Discharged"; }).length, patients.length + " on file") +
    tile("Doctors on duty", onDuty, doctors.length + " on roster") +
    tile("Today's appointments", todayAp.length, appts.filter(function (a) { return a.status === "Pending"; }).length + " pending") +
    tile("Beds available", free + " / " + beds, "ICU: " + icuFree + " free");

  function tile(l, v, m) {
    return '<article class="kpi"><div class="kpi-label">' + l + '</div><div class="kpi-value">' + v + '</div><div class="kpi-meta">' + m + "</div></article>";
  }

  var qbody = document.getElementById("qBody");
  var qmob = document.getElementById("qMob");
  if (!todayAp.length) {
    qbody.innerHTML = '<tr><td colspan="5" class="empty">No appointments today.</td></tr>';
    qmob.innerHTML = '<div class="empty">No appointments today.</div>';
  } else {
    qbody.innerHTML = todayAp.map(function (x) {
      return "<tr><td class='mono'>" + MC.esc(x.id) + "</td><td>" + MC.esc(x.patient) + "</td><td>" +
        MC.esc(MC.doctorName(x.doctorId)) + "</td><td>" + MC.esc(x.time) + "</td><td>" + MC.pill(x.status) + "</td></tr>";
    }).join("");
    qmob.innerHTML = todayAp.map(function (x) {
      return '<article class="m-card"><div class="top"><strong>' + MC.esc(x.patient) + "</strong>" + MC.pill(x.status) +
        "</div><div>" + MC.esc(MC.doctorName(x.doctorId)) + " · " + MC.esc(x.time) + "</div></article>";
    }).join("");
  }

  var sess = MC.session() || {};
  var depts = {};
  invoices.forEach(function (i) {
    if (i.status === "Refund") return;
    depts[i.department] = (depts[i.department] || 0) + Number(i.amount);
  });
  var revTitle = document.getElementById("revenueTitle");
  var revLink = document.getElementById("revenueLink");
  if (sess.role === "admin") {
    if (revTitle) revTitle.textContent = "Revenue share";
    if (revLink) revLink.style.display = "";
    if (MC.mountPie) {
      MC.mountPie(document.getElementById("revBars"), Object.keys(depts).map(function (k, i) {
        return { label: k, value: depts[k], display: MC.inr(depts[k]), color: MC.pieColors[i] };
      }), { title: "", center: "Share", totalDisplay: MC.inr(Object.keys(depts).reduce(function (a, k) { return a + depts[k]; }, 0)) });
    }
  } else {
    if (revTitle) revTitle.textContent = "Beds today";
    if (revLink) { revLink.href = "ward-allotment.html"; revLink.textContent = "Wards"; }
    var types = ["ICU", "Private", "General Ward", "Maternity"];
    if (MC.mountBars) {
      MC.mountBars(document.getElementById("revBars"), types.map(function (t, i) {
        var set = rooms.filter(function (r) { return r.type === t; });
        var o = set.reduce(function (a, r) { return a + (Number(r.occupied) || 0); }, 0);
        return { label: t, value: o, display: String(o), color: MC.pieColors[i] };
      }), { title: "" });
    }
  }

  var admitted = patients.slice(0, 6);
  document.getElementById("adBody").innerHTML = admitted.map(function (p) {
    return "<tr><td>" + MC.esc(p.name) + "</td><td>" + MC.esc(p.department) + "</td><td>" +
      MC.esc(MC.doctorName(p.doctorId)) + "</td><td>" + MC.pill(p.status) + "</td></tr>";
  }).join("");

  document.getElementById("smsList").innerHTML = alerts.slice(0, 5).map(function (a) {
    return '<li class="occ"><div class="occ-top"><div><strong>' + MC.esc(a.template) + '</strong><div class="kpi-meta">' +
      MC.esc(a.to) + " · " + MC.esc(a.time) + "</div></div>" + MC.pill(a.status) + "</div></li>";
  }).join("") || '<p class="empty">No alerts yet.</p>';

  var combined = sess.role === "admin" && MC.adminView() === "combined";
  var card = document.getElementById("adminPatientsCard");
  if (card) {
    card.style.display = combined ? "block" : "none";
    if (combined) {
      document.getElementById("adminPatBody").innerHTML = patients.slice(0, 8).map(function (p) {
        var due = invoices.filter(function (i) {
          return (i.patientId === p.id || i.patient === p.name) && (i.status === "Due" || i.status === "Processing");
        }).reduce(function (a, i) { return a + Number(i.amount || 0); }, 0);
        return "<tr><td class='mono'>" + MC.esc(p.id) + "</td><td>" + MC.esc(p.name) + "</td><td>" +
          MC.pill(p.status) + "</td><td class='mono'>" + MC.inr(due) + "</td></tr>";
      }).join("") || '<tr><td colspan="4" class="empty">No patients.</td></tr>';
    }
  }
  if (window.MCApplyI18n) MCApplyI18n();
});
