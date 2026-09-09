/* ===== PAGE JS: Pharmacy — stock, add, dispense ===== */
MC.ready(function () {
  if (!MC.session()) return;
  var KEY = MC.KEYS.pharmacy;
  function rows() { return MC.get(KEY); }
  function statusOf(r) {
    if (r.stock <= 0) return "Out";
    if (r.stock <= r.min) return "Low";
    return "In-stock";
  }
  function render() {
    var q = (document.getElementById("search").value || "").toLowerCase();
    var list = rows().filter(function (r) { return !q || (r.name + " " + r.batch).toLowerCase().indexOf(q) !== -1; });
    document.getElementById("kpis").innerHTML =
      kpi("SKUs", rows().length, "in formulary") +
      kpi("Low stock", rows().filter(function (r) { return statusOf(r) === "Low"; }).length, "reorder") +
      kpi("Out of stock", rows().filter(function (r) { return statusOf(r) === "Out"; }).length, "blocked") +
      kpi("Units on hand", rows().reduce(function (a, r) { return a + Number(r.stock); }, 0), "across batches");
    document.getElementById("tbody").innerHTML = list.map(function (r) {
      return "<tr><td class='mono'>" + MC.esc(r.id) + "</td><td>" + MC.esc(r.name) + "</td><td>" + MC.esc(r.batch) +
        "</td><td class='mono'>" + r.stock + " " + MC.esc(r.unit) + "</td><td class='mono'>" + Number(r.dispensed || 0) + "</td><td>" + MC.pill(statusOf(r)) +
        "</td><td class='row-actions'><button class='btn btn-primary btn-sm' data-d='" + r.id + "'>" + MC.t("Dispense 1", "Dispense 1") + "</button>" +
        "<button class='btn btn-ghost btn-sm' data-a='" + r.id + "'>Add 10</button></td></tr>";
    }).join("") || '<tr><td colspan="7" class="empty">' + MC.t("No medicines.", "No medicines.") + "</td></tr>";
    document.getElementById("mobileList").innerHTML = list.map(function (r) {
      return '<article class="m-card"><div class="top"><strong>' + MC.esc(r.name) + "</strong>" + MC.pill(statusOf(r)) +
        "</div><div>" + r.stock + " " + MC.esc(r.unit) + " · " + Number(r.dispensed || 0) + " " + MC.t("dispensed", "dispensed") + "</div></article>";
    }).join("");
    drawPies();
    if (window.MCApplyI18n) MCApplyI18n();
  }
  function drawPies() {
    if (!MC.mountPie) return;
    var all = rows().slice().sort(function (a, b) { return Number(b.dispensed || 0) - Number(a.dispensed || 0); });
    var top = all.slice(0, 5);
    var rest = all.slice(5).reduce(function (a, r) { return a + Number(r.dispensed || 0); }, 0);
    var most = all[0] ? Number(all[0].dispensed || 0) : 0;
    var least = all.length ? Number(all[all.length - 1].dispensed || 0) : 0;
    var usedAll = all.reduce(function (a, r) { return a + Number(r.dispensed || 0); }, 0);
    MC.mountChart(document.getElementById("pieUse"), [
      { label: all[0] ? all[0].name : "Most used", value: most, meta: MC.t("Most used", "Most used"), color: "#0F766E" },
      { label: all.length ? all[all.length - 1].name : "Least used", value: least, meta: MC.t("Least used", "Least used"), color: "#BE123C" },
      { label: "Others", value: Math.max(0, usedAll - most - least), color: "#94A3B8" }
    ], { title: "Most used vs least used", center: "Units", totalDisplay: String(usedAll) });
    var share = top.map(function (r, i) {
      return { label: r.name, value: Number(r.dispensed || 0), display: String(r.dispensed || 0), color: MC.pieColors[i] };
    });
    if (rest) share.push({ label: "Others", value: rest, display: String(rest), color: "#94A3B8" });
    MC.mountChart(document.getElementById("pieShare"), share, { title: "Medicine usage share", center: "Top 5", totalDisplay: String(usedAll) });
  }
  function kpi(l, v, m) {
    return '<article class="kpi"><div class="kpi-label">' + l + '</div><div class="kpi-value">' + v + '</div><div class="kpi-meta">' + m + "</div></article>";
  }
  document.getElementById("addForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var name = document.getElementById("pName").value.trim();
    if (!name) return;
    var all = rows();
    all.unshift({
      id: MC.nextId(all, "RX-", 10),
      name: name,
      batch: document.getElementById("pBatch").value.trim() || "B-NEW",
      stock: Number(document.getElementById("pStock").value) || 0,
      min: Number(document.getElementById("pMin").value) || 10,
      unit: document.getElementById("pUnit").value,
      dispensed: 0
    });
    MC.set(KEY, all);
    e.target.reset();
    MC.toast("Medicine added");
    render();
  });
  document.body.addEventListener("click", function (e) {
    var d = e.target.getAttribute("data-d");
    var a = e.target.getAttribute("data-a");
    if (!d && !a) return;
    MC.set(KEY, rows().map(function (r) {
      if (r.id === d) { r.stock = Math.max(0, r.stock - 1); r.dispensed = Number(r.dispensed || 0) + 1; }
      if (r.id === a) r.stock += 10;
      return r;
    }));
    render();
  });
  document.getElementById("search").addEventListener("input", render);
  render();
  document.addEventListener("mc-data", render);
});
