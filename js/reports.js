/* ===== PAGE JS: Reports — live pies from appointments, wards, billing ===== */
MC.ready(function () {
  if (!MC.session()) return;

  function paint() {
    var appts = MC.get(MC.KEYS.appointments);
    var patients = MC.get(MC.KEYS.patients);
    var rooms = MC.get(MC.KEYS.rooms);
    var invoices = MC.get(MC.KEYS.invoices);
    var dx = MC.get(MC.KEYS.diagnostics);
    var today = MC.today();
    var paid = invoices.filter(function (i) { return i.status === "Paid"; });
    var collected = paid.reduce(function (a, i) { return a + Number(i.amount); }, 0);
    var due = invoices.filter(function (i) { return i.status === "Due"; }).reduce(function (a, i) { return a + Number(i.amount); }, 0);
    var beds = rooms.reduce(function (a, r) { return a + Number(r.beds); }, 0);
    var occ = rooms.reduce(function (a, r) { return a + Number(r.occupied || (r.patients || []).length); }, 0);

    document.getElementById("kpis").innerHTML =
      kpi(MC.t("Collections", "Collections"), MC.inr(collected), paid.length + " " + MC.t("paid invoices", "paid invoices")) +
      kpi(MC.t("Outstanding", "Outstanding"), MC.inr(due), MC.t("dues", "dues")) +
      kpi(MC.t("Occupancy", "Occupancy"), (beds ? Math.round(occ / beds * 100) : 0) + "%", occ + " / " + beds + " " + MC.t("beds", "beds")) +
      kpi(MC.t("OPD today", "OPD today"), appts.filter(function (a) { return a.date === today; }).length, MC.t("appointments", "appointments"));

    var deptMap = {};
    patients.forEach(function (p) {
      deptMap[p.department] = deptMap[p.department] || { n: 0, adm: 0 };
      deptMap[p.department].n++;
      if (p.status === "Admitted") deptMap[p.department].adm++;
    });
    document.getElementById("deptBody").innerHTML = Object.keys(deptMap).map(function (k) {
      return "<tr><td>" + MC.esc(k) + "</td><td class='mono'>" + deptMap[k].n + "</td><td class='mono'>" + deptMap[k].adm + "</td></tr>";
    }).join("");

    document.getElementById("billBody").innerHTML = invoices.slice(0, 8).map(function (i) {
      return "<tr><td class='mono'>" + MC.esc(i.id) + "</td><td>" + MC.esc(i.patient) + "</td><td>" + MC.inr(i.amount) + "</td><td>" + MC.pill(i.status) + "</td></tr>";
    }).join("");

    document.getElementById("scanMeta").textContent = dx.filter(function (d) { return d.status === "Done"; }).length + " " + MC.t("completed / ", "completed / ") + dx.length + MC.t(" scheduled", " scheduled");

    if (MC.mountChart) {
      MC.mountChart(document.getElementById("pieDept"), Object.keys(deptMap).map(function (k, i) {
        return { label: k, value: deptMap[k].n, display: String(deptMap[k].n), color: MC.pieColors[i % MC.pieColors.length] };
      }), { title: "Patients by department", center: "Patients", totalDisplay: String(patients.length) });
      var st = { Paid: 0, Due: 0, Processing: 0, Refund: 0 };
      invoices.forEach(function (i) { st[i.status] = (st[i.status] || 0) + Number(i.amount || 0); });
      MC.mountChart(document.getElementById("pieBill"), [
        { label: "Paid", value: st.Paid, display: MC.inr(st.Paid), color: "#047857" },
        { label: "Due", value: st.Due, display: MC.inr(st.Due), color: "#B45309" },
        { label: "Processing", value: st.Processing, display: MC.inr(st.Processing), color: "#1D4ED8" },
        { label: "Refund", value: st.Refund, display: MC.inr(st.Refund), color: "#BE123C" }
      ], { title: "Invoice status", center: "Billed", totalDisplay: MC.inr(st.Paid + st.Due + st.Processing + st.Refund) });
      MC.mountChart(document.getElementById("pieBeds"), [
        { label: "Occupied beds", value: occ, display: String(occ), color: "#BE123C" },
        { label: "Free beds", value: Math.max(0, beds - occ), display: String(Math.max(0, beds - occ)), color: "#0F766E" }
      ], { title: "Bed occupancy", center: "Beds", totalDisplay: String(beds) });
    }
    if (window.MCApplyI18n) MCApplyI18n();
  }
  function kpi(l, v, m) {
    return '<article class="kpi"><div class="kpi-label">' + l + '</div><div class="kpi-value">' + v + '</div><div class="kpi-meta">' + m + "</div></article>";
  }
  paint();
  document.addEventListener("mc-data", paint);
});
