/* ===== PAGE JS: Email & SMS — live send via Resend / MSG91 ===== */
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
        "</td><td>" + MC.fmtDate(a.date) + "</td><td>" + MC.pill(a.status) + "</td><td></td></tr>";
    }).join("") || '<tr><td colspan="6" class="empty">No messages yet.</td></tr>';
    if (window.MCApplyI18n) MCApplyI18n();
  }
  function kpi(l, v, m) {
    return '<article class="kpi"><div class="kpi-label">' + l + '</div><div class="kpi-value">' + v + '</div><div class="kpi-meta">' + m + "</div></article>";
  }

  fetch("/api/features", { credentials: "include" }).then(function (r) { return r.json(); }).then(function (c) {
    var el = document.getElementById("mailStatus");
    if (!el) return;
    if (c.email) el.textContent = "Email live (Resend). SMS " + (c.sms ? "live." : "not configured.");
    else el.textContent = "Email not live — add RESEND_API_KEY on Render, then redeploy.";
  }).catch(function () {});

  document.getElementById("sendForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var to = document.getElementById("nTo").value.trim();
    var channel = document.getElementById("nCh").value;
    var tpl = document.getElementById("nTpl").value;
    var body = document.getElementById("nBody").value.trim() || tpl;
    if (!to) { MC.toast("Add an email or phone", "bad"); return; }
    if (channel === "EMAIL" && to.indexOf("@") < 0) {
      MC.toast("Email needs a Gmail / inbox, e.g. name@gmail.com", "bad");
      return;
    }
    var btn = document.getElementById("nSend");
    btn.disabled = true;
    fetch("/api/notify/send", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ to: to, channel: channel, template: tpl, body: body })
    }).then(function (r) { return r.json().then(function (d) { return { http: r.status, d: d }; }); })
      .then(function (pack) {
        var d = pack.d || {};
        if (d.status === "Delivered") MC.toast("Sent to " + to);
        else MC.toast(d.error || "Not sent — " + (d.status || "Failed"), "bad");
        return fetch("/api/store/alerts", { credentials: "include" }).then(function (r) { return r.json(); });
      }).then(function (list) {
        if (Array.isArray(list)) MC._cache.alerts = list;
        render();
      }).catch(function () { MC.toast("Cannot reach the server", "bad"); })
      .finally(function () { btn.disabled = false; });
  });

  ["search", "fStatus"].forEach(function (id) {
    document.getElementById(id).addEventListener("input", render);
    document.getElementById(id).addEventListener("change", render);
  });
  render();
});
