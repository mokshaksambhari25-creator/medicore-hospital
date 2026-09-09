/* ===== PAGE JS: Payments — invoices, collect, refund, receipt ===== */
MC.ready(function () {
  if (!MC.session()) return;
  var KEY = MC.KEYS.invoices;
  var qMethod = "UPI";

  function rows() { return MC.get(KEY); }
  function nextInv() { return MC.nextId(rows(), "INV-", 77120); }

  function stats() {
    var today = MC.today();
    var collected = rows().filter(function (x) { return x.status === "Paid" && x.date === today; });
    var dues = rows().filter(function (x) { return x.status === "Due"; });
    var ins = rows().filter(function (x) { return x.method === "Insurance" && x.status !== "Refund"; });
    var refunds = rows().filter(function (x) { return x.status === "Refund"; });
    var sum = function (arr) { return arr.reduce(function (a, b) { return a + Number(b.amount); }, 0); };
    return { collected: sum(collected), collectedN: collected.length, dues: sum(dues), duesN: dues.length, ins: sum(ins), insN: ins.length, refunds: sum(refunds), refundsN: refunds.length };
  }

  function filtered() {
    var q = (document.getElementById("search").value || "").toLowerCase();
    var st = document.getElementById("fStatus").value;
    var m = document.getElementById("fMethod").value;
    return rows().filter(function (x) {
      var blob = (x.id + " " + x.patient + " " + x.department).toLowerCase();
      if (q && blob.indexOf(q) === -1) return false;
      if (st && x.status !== st) return false;
      if (m && x.method !== m) return false;
      return true;
    });
  }

  function actions(row) {
    var bits = ["<button class='btn btn-ghost btn-sm' type='button' data-rec='" + row.id + "'>" + MC.t("Receipt", "Receipt") + "</button>"];
    if (row.status === "Due" || row.status === "Processing") bits.unshift("<button class='btn btn-primary btn-sm' type='button' data-pay='" + row.id + "'>" + MC.t("Collect", "Collect") + "</button>");
    if (row.status === "Paid") bits.push("<button class='btn btn-danger btn-sm' type='button' data-ref='" + row.id + "'>" + MC.t("Refund", "Refund") + "</button>");
    bits.push("<button class='btn btn-ghost btn-sm' type='button' data-mail='" + row.id + "'>" + MC.t("Email bill", "Email bill") + "</button>");
    return "<div class='row-actions'>" + bits.join("") + "</div>";
  }

  function render() {
    var s = stats();
    document.getElementById("kpis").innerHTML =
      kpi("Collected Today", MC.inr(s.collected), s.collectedN + " transactions") +
      kpi("Outstanding Dues", MC.inr(s.dues), s.duesN + " invoices") +
      kpi("Insurance Claims", MC.inr(s.ins), s.insN + " in process / paid") +
      kpi("Refunds", MC.inr(s.refunds), s.refundsN + " requests");
    var list = filtered();
    var tb = document.getElementById("tbody");
    var mob = document.getElementById("mobileList");
    if (!list.length) {
      tb.innerHTML = '<tr><td colspan="8" class="empty">No invoices match these filters.</td></tr>';
      mob.innerHTML = '<div class="empty">No invoices match these filters.</div>';
    } else {
      tb.innerHTML = list.map(function (x) {
        return "<tr><td class='mono'>" + MC.esc(x.id) + "</td><td>" + MC.esc(x.patient) + "</td><td>" + MC.esc(x.department) +
          "</td><td class='mono'>" + MC.inr(x.amount) + "</td><td>" + MC.esc(x.method) + "</td><td>" + MC.fmtDate(x.date) +
          "</td><td>" + MC.pill(x.status) + "</td><td>" + actions(x) + "</td></tr>";
      }).join("");
      mob.innerHTML = list.map(function (x) {
        return '<article class="m-card"><div class="top"><strong class="mono">' + MC.esc(x.id) + "</strong>" + MC.pill(x.status) +
          "</div><div>" + MC.esc(x.patient) + " · " + MC.inr(x.amount) + "</div>" + actions(x) + "</article>";
      }).join("");
    }
    document.getElementById("patientList").innerHTML = Array.from(new Set(rows().map(function (x) { return x.patient; })))
      .map(function (n) { return '<option value="' + MC.esc(n) + '">'; }).join("");
    drawPies();
    if (window.MCApplyI18n) MCApplyI18n();
  }

  function drawPies() {
    if (!MC.mountPie) return;
    var all = rows();
    var bySt = { Paid: 0, Due: 0, Processing: 0, Refund: 0 };
    var byM = { UPI: 0, Card: 0, Cash: 0, Insurance: 0 };
    all.forEach(function (x) {
      bySt[x.status] = (bySt[x.status] || 0) + Number(x.amount || 0);
      if (x.status !== "Refund") byM[x.method] = (byM[x.method] || 0) + Number(x.amount || 0);
    });
    MC.mountPie(document.getElementById("pieStatus"), [
      { label: "Paid", value: bySt.Paid, display: MC.inr(bySt.Paid), color: "#047857" },
      { label: "Due", value: bySt.Due, display: MC.inr(bySt.Due), color: "#B45309" },
      { label: "Processing", value: bySt.Processing, display: MC.inr(bySt.Processing), color: "#1D4ED8" },
      { label: "Refund", value: bySt.Refund, display: MC.inr(bySt.Refund), color: "#BE123C" }
    ], "Collections by status");
    MC.mountPie(document.getElementById("pieMethod"), [
      { label: "UPI", value: byM.UPI, display: MC.inr(byM.UPI), color: "#0F766E" },
      { label: "Card", value: byM.Card, display: MC.inr(byM.Card), color: "#1D4ED8" },
      { label: "Cash", value: byM.Cash, display: MC.inr(byM.Cash), color: "#A16207" },
      { label: "Insurance", value: byM.Insurance, display: MC.inr(byM.Insurance), color: "#7C3AED" }
    ], "Collections by method");
  }

  function inWords(n) {
    n = Math.round(Number(n) || 0);
    if (!n) return "Zero rupees only";
    var ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"];
    var tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"];
    function chunk(x) {
      if (x < 20) return ones[x];
      if (x < 100) return tens[Math.floor(x / 10)] + (x % 10 ? " " + ones[x % 10] : "");
      return ones[Math.floor(x / 100)] + " Hundred" + (x % 100 ? " " + chunk(x % 100) : "");
    }
    var cr = Math.floor(n / 10000000);
    var l = Math.floor((n % 10000000) / 100000);
    var th = Math.floor((n % 100000) / 1000);
    var rest = n % 1000;
    var parts = [];
    if (cr) parts.push(chunk(cr) + " Crore");
    if (l) parts.push(chunk(l) + " Lakh");
    if (th) parts.push(chunk(th) + " Thousand");
    if (rest) parts.push(chunk(rest));
    return parts.join(" ") + " rupees only";
  }
  function kpi(l, v, m) {
    return '<article class="kpi"><div class="kpi-label">' + l + '</div><div class="kpi-value">' + v + '</div><div class="kpi-meta">' + m + "</div></article>";
  }

  function showReceipt(id) {
    var x = rows().filter(function (r) { return r.id === id; })[0];
    if (!x) return;
    document.getElementById("receiptBody").innerHTML =
      '<div class="receipt-pro receipt-print">' +
        '<div class="r-head"><img src="img/logo-LIVE.jpg" alt="MediCore" width="52" height="52" />' +
        "<div><h4>" + MC.t("MediCore Hospital", "MediCore Hospital") + "</h4>" +
        "<p>" + MC.t("Sion–Bandra Link Road, Mumbai 400022", "Sion–Bandra Link Road, Mumbai 400022") + "<br>" +
        MC.t("Emergency 022 2416 2400 · Ambulance 108", "Emergency 022 2416 2400 · Ambulance 108") + "</p></div></div>" +
        '<div class="r-row"><span>' + MC.t("Invoice", "Invoice") + "</span><strong>" + MC.esc(x.id) + "</strong></div>" +
        '<div class="r-row"><span>' + MC.t("Patient", "Patient") + "</span><strong>" + MC.esc(x.patient) + (x.patientId ? " · " + MC.esc(x.patientId) : "") + "</strong></div>" +
        '<div class="r-row"><span>' + MC.t("Department", "Department") + "</span><span>" + MC.esc(x.department) + "</span></div>" +
        '<div class="r-row"><span>' + MC.t("Method", "Method") + "</span><span>" + MC.esc(x.method) + "</span></div>" +
        '<div class="r-row"><span>' + MC.t("Date", "Date") + "</span><span>" + MC.fmtDate(x.date) + "</span></div>" +
        '<div class="r-row"><span>' + MC.t("Status", "Status") + "</span><span>" + MC.esc(MC.t(x.status, x.status)) + "</span></div>" +
        '<div class="r-row r-total"><span>' + MC.t("Amount", "Amount") + "</span><span>" + MC.inr(x.amount) + "</span></div>" +
        "<p class='hint' style='margin-top:8px'>" + MC.t("Rupees", "Rupees") + ": " + inWords(x.amount) + "</p>" +
        "<p class='r-foot'>" + MC.t("This is a computer-generated receipt. No signature is required.", "This is a computer-generated receipt. No signature is required.") + "</p>" +
      "</div>";
    MC.openModal("receiptModal");
  }

  document.querySelectorAll("#qMethods .chip").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll("#qMethods .chip").forEach(function (b) { b.classList.remove("on"); });
      btn.classList.add("on");
      qMethod = btn.getAttribute("data-m");
    });
  });

  document.getElementById("quickForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var ref = document.getElementById("qRef").value.trim();
    var amt = Number(document.getElementById("qAmt").value);
    document.getElementById("f-ref").classList.toggle("invalid", !ref);
    document.getElementById("f-amt").classList.toggle("invalid", !(amt > 0));
    if (!ref || !(amt > 0)) return;
    var all = rows();
    var byId = all.filter(function (x) { return x.id.toLowerCase() === ref.toLowerCase(); })[0];
    var byName = all.filter(function (x) { return x.patient.toLowerCase() === ref.toLowerCase() && (x.status === "Due" || x.status === "Processing"); })[0];
    var receiptId;
    var st = qMethod === "Insurance" ? "Processing" : "Paid";
    if (byId && (byId.status === "Due" || byId.status === "Processing")) {
      all = all.map(function (x) { if (x.id === byId.id) { x.status = st; x.method = qMethod; x.amount = amt; x.date = MC.today(); } return x; });
      receiptId = byId.id;
    } else if (byName) {
      all = all.map(function (x) { if (x.id === byName.id) { x.status = st; x.method = qMethod; x.amount = amt; x.date = MC.today(); } return x; });
      receiptId = byName.id;
    } else {
      var match = MC.get(MC.KEYS.patients).filter(function (p) {
        return String(p.name || "").toLowerCase() === ref.toLowerCase() || String(p.id || "").toLowerCase() === ref.toLowerCase();
      })[0];
      var row = {
        id: nextInv(), patient: match ? match.name : ref, patientId: match ? match.id : "",
        department: "General", amount: amt, method: qMethod, date: MC.today(), status: st, notes: "Quick payment"
      };
      all.unshift(row);
      receiptId = row.id;
    }
    MC.set(KEY, all);
    MC.logAlert(ref, "Payment receipt", "Queued");
    MC.toast("Payment recorded");
    e.target.reset();
    qMethod = "UPI";
    document.querySelectorAll("#qMethods .chip").forEach(function (b) { b.classList.toggle("on", b.getAttribute("data-m") === "UPI"); });
    render();
    showReceipt(receiptId);
  });

  document.getElementById("openCreate").addEventListener("click", function () { MC.openModal("createModal"); });
  document.getElementById("createForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var patient = document.getElementById("cPatient").value.trim();
    var amount = Number(document.getElementById("cAmt").value);
    document.getElementById("c-patient").classList.toggle("invalid", !patient);
    document.getElementById("c-amt").classList.toggle("invalid", !(amount > 0));
    if (!patient || !(amount > 0)) return;
    var method = document.getElementById("cMethod").value;
    var all = rows();
    var match = MC.get(MC.KEYS.patients).filter(function (p) {
      return String(p.name || "").toLowerCase() === patient.toLowerCase();
    })[0];
    all.unshift({
      id: nextInv(), patient: patient, patientId: match ? match.id : "",
      department: document.getElementById("cDept").value,
      amount: amount, method: method, date: MC.today(),
      status: method === "Insurance" ? "Processing" : "Due",
      notes: document.getElementById("cNotes").value.trim()
    });
    MC.set(KEY, all);
    MC.closeModal("createModal");
    e.target.reset();
    MC.toast("Invoice created");
    render();
  });

  document.body.addEventListener("click", function (e) {
    var rec = e.target.getAttribute("data-rec");
    var pay = e.target.getAttribute("data-pay");
    var refn = e.target.getAttribute("data-ref");
    var mail = e.target.getAttribute("data-mail");
    if (mail) {
      fetch("/api/invoices/email", {
        method: "POST", credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: mail })
      }).then(function (r) { return r.json(); }).then(function (res) {
        MC.toast(MC.t("Bill mailed", "Bill mailed") + (res.to ? " · " + res.to : "") + (res.demo ? " (queue)" : ""));
      }).catch(function () { MC.toast(MC.t("Cannot reach the server", "Cannot reach the server"), "bad"); });
      return;
    }
    if (rec) showReceipt(rec);
    if (pay) {
      MC.set(KEY, rows().map(function (x) {
        if (x.id === pay) { x.status = x.method === "Insurance" ? "Processing" : "Paid"; x.date = MC.today(); }
        return x;
      }));
      MC.toast(pay + " collected");
      render();
      showReceipt(pay);
    }
    if (refn) {
      if (!confirm("Issue a refund for " + refn + "?")) return;
      MC.set(KEY, rows().map(function (x) { if (x.id === refn) x.status = "Refund"; return x; }));
      MC.toast("Refund recorded");
      render();
    }
  });
  ["search", "fStatus", "fMethod"].forEach(function (id) {
    document.getElementById(id).addEventListener("input", render);
    document.getElementById(id).addEventListener("change", render);
  });
  render();
});
