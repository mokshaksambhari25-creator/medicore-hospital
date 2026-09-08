/* ===== PAGE JS: Email & SMS log ===== */
MC.ready(function () {
  if (!MC.session()) return;
  var KEY = MC.KEYS.alerts;
  function rows() { return MC.get(KEY); }
  function render() {
    var q = (document.getElementById("search").value || "").toLowerCase();
    var st = document.getElementById("fStatus").value;
    var list = rows().filter(function (a) {
      if (q && (a.to + " " + a.template).toLowerCase().indexOf(q) === -1) return false;
      if (st && a.status !== st) return false;
      return true;
    });
    document.getElementById("kpis").innerHTML =
      kpi("Logged", rows().length, "messages") +
      kpi("Delivered", rows().filter(function (a) { return a.status === "Delivered"; }).length, "ok") +
      kpi("Queued", rows().filter(function (a) { return a.status === "Queued"; }).length, "pending") +
      kpi("Failed", rows().filter(function (a) { return a.status === "Failed"; }).length, "retry");
    document.getElementById("tbody").innerHTML = list.map(function (a) {
      return "<tr><td>" + MC.esc(a.to || "—") + "</td><td>" + MC.esc(a.template) + "</td><td>" + MC.esc(a.time) +
        "</td><td>" + MC.fmtDate(a.date) + "</td><td>" + MC.pill(a.status) + "</td><td>" +
        (a.status !== "Delivered" ? "<button class='btn btn-primary btn-sm' data-id='" + a.id + "'>Mark delivered</button>" : "—") +
        "</td></tr>";
    }).join("") || '<tr><td colspan="6" class="empty">No messages yet.</td></tr>';
  }
  function kpi(l, v, m) {
    return '<article class="kpi"><div class="kpi-label">' + l + '</div><div class="kpi-value">' + v + '</div><div class="kpi-meta">' + m + "</div></article>";
  }
  document.getElementById("sendForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var to = document.getElementById("nTo").value.trim();
    var tpl = document.getElementById("nTpl").value;
    if (!to) return;
    MC.logAlert(to, tpl, "Queued");
    e.target.reset();
    MC.toast("Queued to " + to);
    render();
  });
  document.body.addEventListener("click", function (e) {
    var id = e.target.getAttribute("data-id");
    if (!id) return;
    MC.set(KEY, rows().map(function (a) { if (a.id === id) a.status = "Delivered"; return a; }));
    render();
  });
  ["search", "fStatus"].forEach(function (id) {
    document.getElementById(id).addEventListener("input", render);
    document.getElementById(id).addEventListener("change", render);
  });
  render();
});
