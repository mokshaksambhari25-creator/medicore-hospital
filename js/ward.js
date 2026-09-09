/* ===== PAGE JS: Ward Allotment — beds, occupancy, discharge ===== */
MC.ready(function () {
  if (!MC.session()) return;
  var KEY = MC.KEYS.rooms;

  function derive(room) {
    var r = Object.assign({}, room);
    r.patients = Array.isArray(r.patients) ? r.patients.slice() : (r.occupant ? [r.occupant] : []);
    r.occupied = r.patients.length;
    if (r.status === "Cleaning" && r.occupied === 0) { r.occupant = ""; return r; }
    if (r.occupied === 0) { r.status = "Available"; r.occupant = ""; }
    else if (r.occupied >= r.beds) { r.status = "Occupied"; r.occupant = r.beds === 1 ? r.patients[0] : r.occupied + " patients"; }
    else { r.status = "Partially Full"; r.occupant = r.occupied === 1 ? r.patients[0] : r.occupied + " patients"; }
    return r;
  }
  function rows() { return MC.get(KEY).map(derive); }
  function save(list) { MC.set(KEY, list.map(derive)); }
  function freeBeds(r) { return r.status === "Cleaning" ? 0 : Math.max(0, r.beds - r.occupied); }

  function render() {
    var rooms = rows();
    var total = rooms.reduce(function (a, r) { return a + r.beds; }, 0);
    var occ = rooms.reduce(function (a, r) { return a + r.occupied; }, 0);
    var clean = rooms.filter(function (r) { return r.status === "Cleaning"; }).length;
    var avail = rooms.reduce(function (a, r) { return a + freeBeds(r); }, 0);
    var icuFree = rooms.filter(function (r) { return r.type === "ICU"; }).reduce(function (a, r) { return a + freeBeds(r); }, 0);
    document.getElementById("kpis").innerHTML =
      kpi("Total Beds", total, rooms.length + " rooms") +
      kpi("Occupied", occ, (total ? Math.round(occ / total * 100) : 0) + "% occupancy") +
      kpi("Available", avail, "ICU: " + icuFree + " free") +
      kpi("Under Cleaning", clean, "housekeeping");

    var types = ["ICU", "Private", "General Ward", "Maternity"];
    if (MC.mountPie) {
      MC.mountPie(document.getElementById("pieBeds"), [
        { label: "Occupied beds", value: occ, display: String(occ), color: "#BE123C" },
        { label: "Available", value: avail, display: String(avail), color: "#047857" },
        { label: "Under Cleaning", value: rooms.filter(function (r) { return r.status === "Cleaning"; }).reduce(function (a, r) { return a + r.beds; }, 0), color: "#B45309" }
      ], { title: "Beds live", center: "Beds", totalDisplay: String(total) });
      MC.mountBars(document.getElementById("pieTypes"), types.map(function (t, i) {
        var set = rooms.filter(function (r) { return r.type === t; });
        var o = set.reduce(function (a, r) { return a + r.occupied; }, 0);
        return { label: t, value: o, display: o + " beds", color: MC.pieColors[i] };
      }), { title: "Occupied by ward type" });
    }
    document.getElementById("occBars").innerHTML = types.map(function (t) {
      var set = rooms.filter(function (r) { return r.type === t; });
      var beds = set.reduce(function (a, r) { return a + r.beds; }, 0);
      var o = set.reduce(function (a, r) { return a + r.occupied; }, 0);
      var pct = beds ? Math.round(o / beds * 100) : 0;
      var cls = pct >= 85 ? "hot" : pct >= 70 ? "mid" : "";
      return '<div class="occ"><div class="occ-top"><strong>' + t + "</strong><span>" + pct + " % · " + o + "/" + beds +
        '</span></div><div class="bar ' + cls + '"><span style="width:' + pct + '%"></span></div></div>';
    }).join("");

    var q = (document.getElementById("search").value || "").toLowerCase();
    var t = document.getElementById("fType").value;
    var s = document.getElementById("fStatus").value;
    var f = document.getElementById("fFloor").value;
    var list = rooms.filter(function (r) {
      var blob = (r.id + " " + r.type + " " + r.occupant + " " + (r.patients || []).join(" ")).toLowerCase();
      if (q && blob.indexOf(q) === -1) return false;
      if (t && r.type !== t) return false;
      if (s && r.status !== s) return false;
      if (f && r.floor !== f) return false;
      return true;
    });

    function actions(r) {
      var bits = [];
      if (freeBeds(r) > 0) bits.push("<button class='btn btn-primary btn-sm' data-allot='" + r.id + "'>Allot</button>");
      if (r.occupied > 0) bits.push("<button class='btn btn-ghost btn-sm' data-dis='" + r.id + "'>Discharge</button>");
      if (r.status === "Cleaning") bits.push("<button class='btn btn-primary btn-sm' data-ready='" + r.id + "'>Mark available</button>");
      else if (r.occupied === 0 && r.status === "Available") bits.push("<button class='btn btn-ghost btn-sm' data-clean='" + r.id + "'>Mark cleaning</button>");
      return "<div class='row-actions'>" + (bits.join("") || "—") + "</div>";
    }

    document.getElementById("tbody").innerHTML = list.map(function (r) {
      return "<tr><td class='mono'>" + MC.esc(r.id) + "</td><td>" + MC.esc(r.type) + "</td><td>" + MC.esc(r.floor) +
        "</td><td class='mono'>" + r.occupied + "/" + r.beds + "</td><td class='mono'>" + MC.inr(r.tariff) + "/day</td><td>" +
        MC.esc(r.occupant || "—") + "</td><td>" + MC.pill(r.status) + "</td><td>" + actions(r) + "</td></tr>";
    }).join("") || '<tr><td colspan="8" class="empty">No rooms match.</td></tr>';
    document.getElementById("mobileList").innerHTML = list.map(function (r) {
      return '<article class="m-card"><div class="top"><strong>' + MC.esc(r.id) + "</strong>" + MC.pill(r.status) +
        "</div><div>" + MC.esc(r.type) + " · " + r.occupied + "/" + r.beds + "</div>" + actions(r) + "</article>";
    }).join("");

    var open = rooms.filter(function (r) { return freeBeds(r) > 0; });
    document.getElementById("aRoom").innerHTML = open.length
      ? open.map(function (r) { return '<option value="' + r.id + '">' + r.id + " · " + r.type + " · " + freeBeds(r) + " free</option>"; }).join("")
      : '<option value="">No free beds</option>';
    if (window.MCApplyI18n) MCApplyI18n();
    var names = MC.get(MC.KEYS.patients).map(function (p) { return p.name; });
    document.getElementById("knownPatients").innerHTML = names.map(function (n) { return '<option value="' + MC.esc(n) + '">'; }).join("");
  }
  function kpi(l, v, m) {
    return '<article class="kpi"><div class="kpi-label">' + l + '</div><div class="kpi-value">' + v + '</div><div class="kpi-meta">' + m + "</div></article>";
  }

  function openAllot(pre) {
    render();
    if (pre) document.getElementById("aRoom").value = pre;
    document.getElementById("aAdmit").value = MC.today();
    MC.openModal("allotModal");
  }

  document.getElementById("openAllot").addEventListener("click", function () { openAllot(); });
  document.getElementById("openAddBed").addEventListener("click", function () { MC.openModal("addBedModal"); });
  document.getElementById("addBedForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var id = document.getElementById("bId").value.trim().toUpperCase();
    var beds = Number(document.getElementById("bBeds").value) || 1;
    var tariff = Number(document.getElementById("bTariff").value) || 0;
    var exists = rows().some(function (r) { return r.id.toUpperCase() === id; });
    document.getElementById("b-id").classList.toggle("invalid", !id || exists);
    if (!id || exists) return;
    var all = rows();
    all.push({
      id: id,
      type: document.getElementById("bType").value,
      floor: document.getElementById("bFloor").value,
      beds: beds,
      occupied: 0,
      tariff: tariff,
      occupant: "",
      status: "Available",
      patients: []
    });
    save(all);
    MC.closeModal("addBedModal");
    e.target.reset();
    document.getElementById("bBeds").value = "1";
    document.getElementById("bTariff").value = "6500";
    MC.toast(id + " added to the register");
    render();
  });
  document.getElementById("allotForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var patient = document.getElementById("aPatient").value.trim();
    var rid = document.getElementById("aRoom").value;
    document.getElementById("a-patient").classList.toggle("invalid", !patient);
    document.getElementById("a-room").classList.toggle("invalid", !rid);
    if (!patient || !rid) return;
    var rooms = rows();
    var taken = rooms.some(function (r) { return (r.patients || []).some(function (p) { return p.toLowerCase() === patient.toLowerCase(); }); });
    if (taken) { MC.toast(patient + " already has a bed", "bad"); return; }
    var room = rooms.filter(function (r) { return r.id === rid; })[0];
    if (!room || freeBeds(room) <= 0) { MC.toast("No free bed", "bad"); return; }
    room.patients.push(patient);
    save(rooms.map(function (r) { return r.id === rid ? room : r; }));
    MC.closeModal("allotModal");
    e.target.reset();
    MC.toast(patient + " allotted to " + rid);
    render();
  });

  document.body.addEventListener("click", function (e) {
    var allot = e.target.getAttribute("data-allot");
    var dis = e.target.getAttribute("data-dis");
    var ready = e.target.getAttribute("data-ready");
    var clean = e.target.getAttribute("data-clean");
    if (allot) openAllot(allot);
    if (dis) {
      var room = rows().filter(function (r) { return r.id === dis; })[0];
      if (!room || !room.occupied) return;
      var name = room.patients[room.patients.length - 1];
      if (room.patients.length > 1) {
        var pick = prompt("Discharge which patient?\n" + room.patients.join("\n"), name);
        if (pick === null) return;
        var found = room.patients.filter(function (p) { return p.toLowerCase() === pick.trim().toLowerCase(); })[0];
        if (!found) { MC.toast("Name not on this room", "bad"); return; }
        name = found;
      } else if (!confirm("Discharge " + name + " from " + dis + "?")) return;
      room.patients = room.patients.filter(function (p) { return p !== name; });
      if (!room.patients.length) room.status = "Cleaning";
      save(rows().map(function (r) { return r.id === dis ? room : r; }));
      MC.toast(name + " discharged");
      render();
    }
    if (ready) {
      save(rows().map(function (r) { if (r.id === ready) { r.status = "Available"; r.patients = []; } return r; }));
      render();
    }
    if (clean) {
      save(rows().map(function (r) { if (r.id === clean) { r.status = "Cleaning"; r.patients = []; } return r; }));
      render();
    }
  });
  ["search", "fType", "fStatus", "fFloor"].forEach(function (id) {
    document.getElementById(id).addEventListener("input", render);
    document.getElementById(id).addEventListener("change", render);
  });
  render();
  document.addEventListener("mc-data", render);
});
