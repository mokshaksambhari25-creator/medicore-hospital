/* ===== PAGE JS: Email & SMS — templates + custom body, Gmail if smtp.env ===== */
MC.ready(function () {
  if (!MC.session()) return;
  var KEY = MC.KEYS.alerts;
  var BODIES = {
    "Appointment reminder": "Namaste, this is MediCore Hospital. Your appointment is confirmed. Please arrive 15 minutes early. Reply STOP to opt out.",
    "Report ready": "Namaste, your diagnostic report is ready at MediCore. Please sign in to the patient portal or collect it from reception.",
    "Payment due": "Namaste, a hospital bill is due at MediCore. Sign in to the patient portal to pay by UPI or card, or visit the billing desk.",
    "Payment receipt": "Namaste, we have received your payment at MediCore Hospital. Thank you. Keep this message as a receipt note.",
    "Scan slot changed": "Namaste, your scan slot at MediCore has changed. Please check the new time with reception or your patient portal.",
    "Ward ready": "Namaste, a bed / ward is ready for you at MediCore Hospital. Please contact reception.",
    "Discharge summary": "Namaste, your discharge summary is ready at MediCore. Collect papers from the ward desk.",
    "Pharmacy ready": "Namaste, your medicines are packed at the MediCore pharmacy. Please collect them with your prescription.",
    "Custom": ""
  };

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

  fetch("/api/features", { credentials: "include" }).then(function (r) { return r.json(); }).then(function (f) {
    var hint = document.getElementById("mailHint");
    if (!hint) return;
    if (f && f.email) hint.textContent = "Gmail is connected. Email will send for real.";
    else hint.textContent = "Gmail not connected yet. Copy SERVER/smtp.env.example to smtp.env and add your Gmail App Password. Until then, messages are logged as demo.";
  }).catch(function () {});

  function fillBody() {
    var tpl = document.getElementById("nTpl").value;
    document.getElementById("nBody").value = BODIES[tpl] != null ? BODIES[tpl] : "";
  }
  document.getElementById("nTpl").addEventListener("change", fillBody);
  fillBody();

  document.getElementById("sendForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var to = document.getElementById("nTo").value.trim();
    var tpl = document.getElementById("nTpl").value;
    var body = document.getElementById("nBody").value.trim();
    var channel = document.getElementById("nChannel").value;
    if (!to) { MC.toast("Add an email or phone", "bad"); return; }
    var btn = document.getElementById("sendBtn");
    if (btn) btn.disabled = true;
    fetch("/api/notify/send", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ to: to, template: tpl, body: body || tpl, channel: channel })
    }).then(function (r) { return r.json(); }).then(function (res) {
      if (btn) btn.disabled = false;
      if (!res.ok) { MC.toast(res.error || "Could not send", "bad"); return; }
      MC.toast(res.demo ? ("Logged (demo): " + tpl) : ("Sent: " + tpl));
      return fetch("/api/bootstrap", { credentials: "include" }).then(function (r) { return r.json(); });
    }).then(function (pack) {
      if (pack && pack.data && pack.data.alerts) MC._cache.alerts = pack.data.alerts;
      render();
    }).catch(function () {
      if (btn) btn.disabled = false;
      MC.logAlert(to, channel + " · " + tpl, "Queued");
      MC.toast("Logged locally");
      render();
    });
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
