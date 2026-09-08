/* ===== PAGE JS: Reports — derived from live stores ===== */
MC.ready(function () {
  if (!MC.session()) return;
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
    kpi("Collections", MC.inr(collected), paid.length + " paid invoices") +
    kpi("Outstanding", MC.inr(due), "dues") +
    kpi("Occupancy", (beds ? Math.round(occ / beds * 100) : 0) + "%", occ + " / " + beds + " beds") +
    kpi("OPD today", appts.filter(function (a) { return a.date === today; }).length, "appointments");

  document.getElementById("deptBody").innerHTML = (function () {
    var map = {};
    patients.forEach(function (p) { map[p.department] = map[p.department] || { n: 0, adm: 0 }; map[p.department].n++; if (p.status === "Admitted") map[p.department].adm++; });
    return Object.keys(map).map(function (k) {
      return "<tr><td>" + MC.esc(k) + "</td><td class='mono'>" + map[k].n + "</td><td class='mono'>" + map[k].adm + "</td></tr>";
    }).join("");
  })();

  document.getElementById("billBody").innerHTML = invoices.slice(0, 8).map(function (i) {
    return "<tr><td class='mono'>" + MC.esc(i.id) + "</td><td>" + MC.esc(i.patient) + "</td><td>" + MC.inr(i.amount) + "</td><td>" + MC.pill(i.status) + "</td></tr>";
  }).join("");

  document.getElementById("scanMeta").textContent = dx.filter(function (d) { return d.status === "Done"; }).length + " completed / " + dx.length + " scheduled";
});
function kpi(l, v, m) {
  return '<article class="kpi"><div class="kpi-label">' + l + '</div><div class="kpi-value">' + v + '</div><div class="kpi-meta">' + m + "</div></article>";
}
