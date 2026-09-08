/* ===== PAGE JS: Patients — register, search, update status ===== */
MC.ready(function () {
  if (!MC.session()) return;
  var KEY = MC.KEYS.patients;

  function rows() { return MC.get(KEY); }

  function doctorSelect(id) {
    return MC.get(MC.KEYS.doctors).map(function (d) {
      return '<option value="' + d.id + '"' + (d.id === id ? " selected" : "") + ">" + MC.esc(d.name) + "</option>";
    }).join("");
  }

  function render() {
    var q = (document.getElementById("search").value || "").toLowerCase();
    var st = document.getElementById("fStatus").value;
    var list = rows().filter(function (p) {
      var blob = (p.id + " " + p.name + " " + p.phone + " " + p.department).toLowerCase();
      if (q && blob.indexOf(q) === -1) return false;
      if (st && p.status !== st) return false;
      return true;
    });
    document.getElementById("kpis").innerHTML =
      kpi("Total", rows().length, "on file") +
      kpi("Admitted", rows().filter(function (p) { return p.status === "Admitted"; }).length, "in wards") +
      kpi("Observation", rows().filter(function (p) { return p.status === "Observation"; }).length, "watch") +
      kpi("Discharged", rows().filter(function (p) { return p.status === "Discharged"; }).length, "closed");

    var tb = document.getElementById("tbody");
    var mob = document.getElementById("mobileList");
    if (!list.length) {
      tb.innerHTML = '<tr><td colspan="8" class="empty">No patients match.</td></tr>';
      mob.innerHTML = '<div class="empty">No patients match.</div>';
      return;
    }
    tb.innerHTML = list.map(function (p) {
      return "<tr><td class='mono'>" + MC.esc(p.id) + "</td><td>" + MC.esc(p.name) + "</td><td>" + p.age + " / " + MC.esc(p.gender) +
        "</td><td>" + MC.esc(p.phone) + "</td><td>" + MC.esc(p.department) + "</td><td>" + MC.esc(MC.doctorName(p.doctorId)) +
        "</td><td>" + MC.pill(p.status) + "</td><td class='row-actions'>" +
        "<button class='btn btn-ghost btn-sm' type='button' data-edit='" + p.id + "'>Edit</button>" +
        "<a class='btn btn-ghost btn-sm' href='ward-allotment.html'>Ward</a>" +
        "<a class='btn btn-ghost btn-sm' href='payment.html'>Bill</a></td></tr>";
    }).join("");
    mob.innerHTML = list.map(function (p) {
      return '<article class="m-card"><div class="top"><strong>' + MC.esc(p.name) + "</strong>" + MC.pill(p.status) +
        "</div><div>" + MC.esc(p.id) + " · " + MC.esc(p.department) + "</div>" +
        "<div class='row-actions' style='margin-top:8px'><button class='btn btn-ghost btn-sm' data-edit='" + p.id + "'>Edit</button></div></article>";
    }).join("");
  }
  function kpi(l, v, m) {
    return '<article class="kpi"><div class="kpi-label">' + l + '</div><div class="kpi-value">' + v + '</div><div class="kpi-meta">' + m + "</div></article>";
  }

  document.getElementById("cDoctor").innerHTML = doctorSelect();
  document.getElementById("openCreate").addEventListener("click", function () {
    document.getElementById("editId").value = "";
    document.getElementById("createForm").reset();
    document.getElementById("modalTitle").textContent = "Register patient";
    MC.openModal("createModal");
  });
  document.body.addEventListener("click", function (e) {
    var id = e.target.getAttribute("data-edit");
    if (!id) return;
    var p = rows().filter(function (x) { return x.id === id; })[0];
    if (!p) return;
    document.getElementById("editId").value = p.id;
    document.getElementById("cName").value = p.name;
    document.getElementById("cAge").value = p.age;
    document.getElementById("cGender").value = p.gender;
    document.getElementById("cPhone").value = p.phone;
    document.getElementById("cEmail").value = p.email || "";
    document.getElementById("cBlood").value = p.blood;
    document.getElementById("cDept").value = p.department;
    document.getElementById("cDoctor").innerHTML = doctorSelect(p.doctorId);
    document.getElementById("cStatus").value = p.status;
    document.getElementById("modalTitle").textContent = "Update " + p.name;
    MC.openModal("createModal");
  });

  document.getElementById("createForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var name = document.getElementById("cName").value.trim();
    if (!name) { document.getElementById("f-name").classList.add("invalid"); return; }
    var all = rows();
    var eid = document.getElementById("editId").value;
    var payload = {
      name: name,
      age: Number(document.getElementById("cAge").value) || 0,
      gender: document.getElementById("cGender").value,
      phone: document.getElementById("cPhone").value.trim(),
      email: document.getElementById("cEmail").value.trim(),
      blood: document.getElementById("cBlood").value.trim() || "—",
      department: document.getElementById("cDept").value,
      doctorId: document.getElementById("cDoctor").value,
      status: document.getElementById("cStatus").value
    };
    if (eid) {
      var prev = all.filter(function (x) { return x.id === eid; })[0] || {};
      var row = Object.assign({}, prev, payload, { id: eid, ward: prev.ward || "" });
      MC.set(KEY, all.map(function (x) { return x.id === eid ? row : x; }));
      MC.closeModal("createModal");
      MC.toast("Patient updated");
      render();
      return;
    }
    fetch("/api/patients", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    }).then(function (r) { return r.json(); }).then(function (res) {
      if (!res.ok || !res.patient) {
        MC.toast((res && res.error) || "Could not register", "bad");
        return;
      }
      all.unshift(res.patient);
      MC._cache[KEY] = all;
      MC.closeModal("createModal");
      document.getElementById("credBox").innerHTML =
        "Patient ID <code>" + MC.esc(res.patient.id) + "</code><br>Password <code>" + MC.esc(res.password) + "</code>";
      MC.openModal("credModal");
      MC.toast("Patient registered · portal login created");
      render();
    }).catch(function () { MC.toast("Cannot reach the server", "bad"); });
  });

  ["search", "fStatus"].forEach(function (id) {
    document.getElementById(id).addEventListener("input", render);
    document.getElementById(id).addEventListener("change", render);
  });
  render();
});
