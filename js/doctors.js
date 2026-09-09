/* ===== PAGE JS: Doctors — add, edit name, off duty, remove ===== */
MC.ready(function () {
  if (!MC.session()) return;
  var KEY = MC.KEYS.doctors;
  var DEPTS = ["Cardiology", "General Medicine", "Orthopaedics", "Neurology", "Paediatrics", "Oncology", "Maternity", "Dermatology"];
  var me = MC.session() || {};

  function rows() { return MC.get(KEY); }

  function grantLogin(id) {
    return fetch("/api/staff-login", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id })
    }).then(function (r) { return r.json(); });
  }

  function revokeLogin(id) {
    return fetch("/api/staff-login/" + encodeURIComponent(id), {
      method: "DELETE",
      credentials: "include"
    }).then(function (r) { return r.json(); });
  }

  function render() {
    var q = (document.getElementById("search").value || "").toLowerCase();
    var list = rows().filter(function (d) {
      return !q || (d.id + " " + d.name + " " + d.department).toLowerCase().indexOf(q) !== -1;
    });
    document.getElementById("kpis").innerHTML =
      kpi("On roster", rows().length, "doctors") +
      kpi("Can sign in", rows().filter(function (d) { return d.login; }).length, "staff IDs") +
      kpi("Available", rows().filter(function (d) { return d.available; }).length, "on duty") +
      kpi("Off duty", rows().filter(function (d) { return !d.available; }).length, "hidden from booking");

    var tb = document.getElementById("tbody");
    var mob = document.getElementById("mobileList");
    function actions(d) {
      var bits = [
        "<button class='btn btn-ghost btn-sm' data-toggle='" + d.id + "'>" + (d.available ? "Set off duty" : "Set available") + "</button>"
      ];
      if (MC.isAdmin()) {
        bits.unshift("<button class='btn btn-primary btn-sm' data-edit='" + d.id + "'>Edit</button>");
        if (d.id !== me.id) bits.push("<button class='btn btn-danger btn-sm' data-del='" + d.id + "'>Remove</button>");
      }
      return "<div class='row-actions'>" + bits.join("") + "</div>";
    }
    tb.innerHTML = list.map(function (d) {
      return "<tr><td class='mono'>" + MC.esc(d.id) + "</td><td><strong>" + MC.esc(d.name) + "</strong>" +
        (d.login ? ' <span class="pill pill-available">Login</span>' : "") +
        (d.id === me.id ? ' <span class="pill pill-processing">You</span>' : "") +
        "</td><td>" + MC.esc(d.department) +
        "</td><td>" + MC.esc(d.phone) + "</td><td>" + MC.pill(d.available ? "Available" : "Off duty") +
        "</td><td>" + actions(d) + "</td></tr>";
    }).join("");
    mob.innerHTML = list.map(function (d) {
      return '<article class="m-card"><div class="top"><strong>' + MC.esc(d.name) + "</strong>" + MC.pill(d.available ? "Available" : "Off duty") +
        "</div><div class='mono'>" + MC.esc(d.id) + " · " + MC.esc(d.department) + "</div>" + actions(d) + "</article>";
    }).join("");
    if (window.MCApplyI18n) MCApplyI18n();
  }
  function kpi(l, v, m) {
    return '<article class="kpi"><div class="kpi-label">' + l + '</div><div class="kpi-value">' + v + '</div><div class="kpi-meta">' + m + "</div></article>";
  }

  document.getElementById("cDept").innerHTML = DEPTS.map(function (x) { return "<option>" + x + "</option>"; }).join("");

  var openCreate = document.getElementById("openCreate");
  if (openCreate) {
    if (!MC.isAdmin()) openCreate.style.display = "none";
    openCreate.addEventListener("click", function () {
      document.getElementById("editId").value = "";
      document.getElementById("createForm").reset();
      document.getElementById("loginField").style.display = "block";
      document.getElementById("cIdLock").textContent = "A new Staff ID is created automatically (DOC-1007, DOC-1008, …). Tick the box if they should be able to sign in.";
      document.getElementById("modalTitle").textContent = "Add doctor";
      document.getElementById("saveBtn").textContent = "Add doctor";
      MC.openModal("createModal");
    });
  }

  document.body.addEventListener("click", function (e) {
    var tid = e.target.getAttribute("data-toggle");
    if (tid) {
      MC.set(KEY, rows().map(function (d) {
        if (d.id === tid) d.available = !d.available;
        return d;
      }));
      MC.toast(tid + " availability updated");
      render();
      return;
    }

    var del = e.target.getAttribute("data-del");
    if (del) {
      if (!MC.isAdmin()) { MC.toast("Only the administrator can remove a doctor", "bad"); return; }
      if (del === me.id) { MC.toast("You cannot remove your own account", "bad"); return; }
      var doc = rows().filter(function (x) { return x.id === del; })[0];
      if (!doc) return;
      if (!confirm("Remove " + doc.name + " (" + del + ") from the roster?")) return;
      var next = function () {
        MC.set(KEY, rows().filter(function (d) { return d.id !== del; }));
        MC.toast(doc.name + " removed");
        render();
      };
      if (doc.login) {
        revokeLogin(del).then(function (res) {
          if (!res.ok) { MC.toast(res.error || "Could not remove login", "bad"); return; }
          next();
        }).catch(function () { MC.toast("Server error", "bad"); });
      } else {
        next();
      }
      return;
    }

    var id = e.target.getAttribute("data-edit");
    if (!id) return;
    if (!MC.isAdmin()) return;
    var d = rows().filter(function (x) { return x.id === id; })[0];
    if (!d) return;
    document.getElementById("editId").value = d.id;
    document.getElementById("cName").value = d.name;
    document.getElementById("cDept").value = d.department;
    document.getElementById("cPhone").value = d.phone;
    document.getElementById("loginField").style.display = "none";
    document.getElementById("cIdLock").textContent = d.login
      ? d.id + " can sign in. You can change the name shown in the hospital — the Staff ID stays the same."
      : d.id + " is on the roster only (no staff login).";
    document.getElementById("modalTitle").textContent = "Update " + d.name;
    document.getElementById("saveBtn").textContent = "Save";
    MC.openModal("createModal");
  });

  document.getElementById("createForm").addEventListener("submit", function (e) {
    e.preventDefault();
    if (!MC.isAdmin()) { MC.toast("Only the administrator can change the roster", "bad"); return; }
    var name = document.getElementById("cName").value.trim();
    if (!name) { document.getElementById("f-name").classList.add("invalid"); return; }
    if (name.toLowerCase().indexOf("dr") !== 0) name = "Dr. " + name.replace(/^dr\.?\s*/i, "");
    var all = rows();
    var eid = document.getElementById("editId").value;
    if (eid) {
      all = all.map(function (d) {
        if (d.id !== eid) return d;
        d.name = name;
        d.department = document.getElementById("cDept").value;
        d.phone = document.getElementById("cPhone").value.trim();
        return d;
      });
      MC.set(KEY, all);
      MC.refreshSessionName();
      MC.toast("Doctor saved");
      MC.closeModal("createModal");
      render();
      return;
    }
    var canLogin = document.getElementById("cLogin").checked;
    var newId = MC.nextId(all, "DOC-", 1007);
    all.push({
      id: newId,
      name: name,
      department: document.getElementById("cDept").value,
      phone: document.getElementById("cPhone").value.trim(),
      available: true,
      login: canLogin
    });
    var finish = function () {
      MC.set(KEY, all);
      MC.closeModal("createModal");
      MC.toast(canLogin ? (name + " added · Staff ID " + newId) : (name + " added to roster"));
      render();
    };
    if (canLogin) {
      grantLogin(newId).then(function (res) {
        if (!res.ok) { MC.toast(res.error || "Could not create login", "bad"); return; }
        finish();
      }).catch(function () { MC.toast("Server error", "bad"); });
    } else {
      finish();
    }
  });

  document.getElementById("search").addEventListener("input", render);
  render();
});
