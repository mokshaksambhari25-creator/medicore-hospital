/* ===== AUTH — staff / patient / admin against Flask ===== */
(function (w) {
  "use strict";
  var MC = w.MC || (w.MC = {});

  MC.session = function () { return MC._me || null; };

  MC.initials = function (name) {
    var parts = String(name || "").replace(/^Dr\.?\s*/i, "").trim().split(/\s+/);
    var a = (parts[0] || "M").charAt(0);
    var b = (parts[1] || "C").charAt(0);
    return (a + b).toUpperCase();
  };

  MC.homeFor = function (user) {
    if (user && user.role === "patient") return "patient.html";
    return "dashboard.html";
  };

  MC.login = function (id, password, role) {
    return fetch("/api/login", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: String(id || "").trim(),
        password: String(password || ""),
        role: String(role || "staff")
      })
    }).then(function (r) {
      return r.json().then(function (data) {
        if (!r.ok || !data.ok) {
          return { ok: false, error: (data && data.error) || "Invalid ID or password" };
        }
        MC._me = data.user;
        if (data.user && data.user.role === "admin") {
          try { sessionStorage.setItem("mc_admin_view", "combined"); } catch (e) {}
        }
        return { ok: true, session: data.user };
      });
    }).catch(function () {
      return { ok: false, error: "Cannot reach the hospital server." };
    });
  };

  MC.logout = function () {
    fetch("/api/logout", { method: "POST", credentials: "include" }).finally(function () {
      MC._me = null;
      try { sessionStorage.removeItem("mc_admin_view"); } catch (e) {}
      location.href = "index.html";
    });
  };

  MC.requireAuth = function () {
    if (MC._me) return MC._me;
    location.href = "login.html";
    return null;
  };

  MC.requireStaff = function () {
    var s = MC.requireAuth();
    if (!s) return null;
    if (s.role === "patient") {
      location.href = "patient.html";
      return null;
    }
    return s;
  };

  MC.requirePatient = function () {
    var s = MC.requireAuth();
    if (!s) return null;
    if (s.role !== "patient") {
      location.href = "dashboard.html";
      return null;
    }
    return s;
  };

  MC.refreshSessionName = function () {
    var s = MC.session();
    if (!s) return s;
    if (s.role === "staff") {
      var doc = MC.getDoctor(s.id);
      if (doc) {
        s.name = doc.name;
        s.department = doc.department;
        MC._me = s;
      }
    }
    return s;
  };
})(window);
