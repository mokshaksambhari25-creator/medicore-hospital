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
        "</td><td class='mono'>" + r.stock + " " + MC.esc(r.unit) + "</td><td>" + MC.pill(statusOf(r)) +
        "</td><td class='row-actions'><button class='btn btn-primary btn-sm' data-d='" + r.id + "'>Dispense 1</button>" +
        "<button class='btn btn-ghost btn-sm' data-a='" + r.id + "'>Add 10</button></td></tr>";
    }).join("") || '<tr><td colspan="6" class="empty">No medicines.</td></tr>';
    document.getElementById("mobileList").innerHTML = list.map(function (r) {
      return '<article class="m-card"><div class="top"><strong>' + MC.esc(r.name) + "</strong>" + MC.pill(statusOf(r)) +
        "</div><div>" + r.stock + " " + MC.esc(r.unit) + "</div></article>";
    }).join("");
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
      unit: document.getElementById("pUnit").value
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
      if (r.id === d) r.stock = Math.max(0, r.stock - 1);
      if (r.id === a) r.stock += 10;
      return r;
    }));
    render();
  });
  document.getElementById("search").addEventListener("input", render);
  render();
});
