/* ===== DATA — SQLite via Flask API, in-memory cache for the UI =====
   Saves go to local MySQL (python app.py). MC.get / MC.set stay synchronous.
*/
(function (w) {
  "use strict";
  var MC = w.MC || (w.MC = {});

  MC.KEYS = {
    doctors: "doctors",
    patients: "patients",
    appointments: "appointments",
    pharmacy: "pharmacy",
    rooms: "rooms",
    invoices: "invoices",
    diagnostics: "diagnostics",
    alerts: "alerts"
  };

  MC._cache = {};
  MC._ready = false;
  MC._waiters = [];
  MC._online = true;

  function storeName(key) {
    if (!key) return key;
    return String(key).replace(/^medicore_/, "");
  }

  MC.inr = function (n) { return "₹" + Number(n || 0).toLocaleString("en-IN"); };
  MC.today = function () { return new Date().toISOString().slice(0, 10); };
  MC.fmtDate = function (iso) {
    if (!iso) return "—";
    var d = new Date(String(iso).slice(0, 10) + "T00:00:00");
    return d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
  };
  MC.esc = function (s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  };
  MC.pill = function (status) {
    var cls = String(status || "").toLowerCase().replace(/\s+/g, "-");
    var label = (MC.t && MC.lang && MC.lang() === "hi") ? MC.t(status, status) : status;
    return '<span class="pill pill-' + cls + '">' + MC.esc(label) + "</span>";
  };

  MC.get = function (key) {
    var name = storeName(key);
    var rows = MC._cache[name];
    return Array.isArray(rows) ? rows : [];
  };

  MC.set = function (key, rows) {
    var name = storeName(key);
    MC._cache[name] = rows;
    try {
      var raw = sessionStorage.getItem("mc_boot");
      if (raw) {
        var boot = JSON.parse(raw);
        if (boot && boot.data) {
          boot.data[name] = rows;
          boot.t = Date.now();
          sessionStorage.setItem("mc_boot", JSON.stringify(boot));
        }
      }
    } catch (e) {}
    if (!MC._online) return rows;
    fetch("/api/store/" + encodeURIComponent(name), {
      method: "PUT",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(rows)
    }).catch(function () {
      MC._online = false;
    });
    return rows;
  };

  MC.nextId = function (rows, prefix, start) {
    var nums = (rows || []).map(function (x) {
      return parseInt(String(x.id).replace(/\D/g, ""), 10);
    }).filter(Boolean);
    var n = (nums.length ? Math.max.apply(null, nums) : (start || 1000) - 1) + 1;
    return prefix + n;
  };

  MC.getDoctor = function (id) {
    return MC.get(MC.KEYS.doctors).filter(function (d) { return d.id === id; })[0] || null;
  };
  MC.doctorName = function (id) {
    var d = MC.getDoctor(id);
    return d ? d.name : id;
  };

  MC.logAlert = function (to, template, status) {
    var rows = MC.get(MC.KEYS.alerts).slice();
    rows.unshift({
      id: "AL-" + Date.now(),
      to: to,
      template: template,
      time: new Date().toTimeString().slice(0, 5),
      date: MC.today(),
      status: status || "Queued"
    });
    MC.set(MC.KEYS.alerts, rows.slice(0, 80));
  };

  MC.ready = function (fn) {
    if (MC._ready) fn();
    else MC._waiters.push(fn);
  };

  function flush() {
    MC._ready = true;
    MC._waiters.splice(0).forEach(function (fn) {
      try { fn(); } catch (e) { console.error(e); }
    });
  }

  function applyBoot(data) {
    if (!data) return;
    Object.keys(data).forEach(function (k) {
      if (k !== "user") MC._cache[k] = data[k];
    });
    if (data.user) MC._me = data.user;
  }

  function saveBoot(data) {
    try {
      sessionStorage.setItem("mc_boot", JSON.stringify({ t: Date.now(), data: data }));
    } catch (e) {}
  }

  function readBoot() {
    try {
      var boot = JSON.parse(sessionStorage.getItem("mc_boot") || "null");
      if (boot && boot.data && Date.now() - (boot.t || 0) < 120000) return boot.data;
    } catch (e) {}
    return null;
  }

  MC.boot = function () {
    var auth = (document.body && document.body.getAttribute("data-auth")) || "public";
    function load(url) {
      return fetch(url, { credentials: "include" }).then(function (r) { return r.json(); });
    }
    if (auth === "public") {
      return load("/api/me").then(function (me) {
        MC._me = me && me.user ? me.user : null;
        flush();
      }).catch(function () { flush(); });
    }
    return load("/api/me")
      .then(function (me) {
        MC._me = me && me.user ? me.user : null;
        if (!MC._me) { flush(); return; }
        if (auth === "patient" && MC._me.role === "patient") {
          return load("/api/patient/home").then(function (pack) {
            if (pack && pack.ok) {
              MC._patientHome = pack;
              if (pack.user) MC._me = pack.user;
            }
            flush();
          });
        }
        if (auth === "staff" && (MC._me.role === "staff" || MC._me.role === "admin")) {
          var cached = readBoot();
          if (cached) {
            applyBoot(cached);
            flush();
            load("/api/bootstrap").then(function (pack) {
              if (pack && pack.ok && pack.data) {
                applyBoot(pack.data);
                saveBoot(pack.data);
                document.dispatchEvent(new Event("mc-data"));
              }
            }).catch(function () {});
            return;
          }
          return load("/api/bootstrap").then(function (pack) {
            if (pack && pack.ok && pack.data) {
              applyBoot(pack.data);
              saveBoot(pack.data);
            }
            flush();
          });
        }
        flush();
      })
      .catch(function () {
        MC._online = false;
        var cached = readBoot();
        if (cached) applyBoot(cached);
        flush();
      });
  };

  MC.ensureSeed = function () {};
})(window);
