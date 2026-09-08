/* ===== APP — sidebar, header, toasts, public nav, admin view switch =====
   Staff pages:   data-auth="staff"
   Patient pages: data-auth="patient"
   Home:          data-auth="home"
   Login:         data-auth="public"
*/
(function (w) {
  "use strict";
  var MC = w.MC || (w.MC = {});

  MC.NAV = [
    { href: "index.html", label: "Home", key: "nav.home" },
    { href: "dashboard.html", label: "Dashboard", key: "nav.dash" },
    { href: "patients.html", label: "Patients", key: "nav.patients" },
    { href: "doctors.html", label: "Doctors", key: "nav.doctors" },
    { href: "appointments.html", label: "Appointments", key: "nav.appts" },
    { href: "pharmacy.html", label: "Pharmacy", key: "nav.pharm" },
    { href: "ward-allotment.html", label: "Ward Allotment", key: "nav.ward" },
    { href: "diagnostics.html", label: "Diagnostics", key: "nav.dx" },
    { href: "payment.html", label: "Payments", key: "nav.pay" },
    { href: "reports.html", label: "Reports", key: "nav.reports" },
    { href: "notifications.html", label: "Email & SMS", key: "nav.alerts" }
  ];

  MC.I18N = {
    en: {
      "nav.home": "Home", "nav.about": "About", "nav.depts": "Departments", "nav.facilities": "Facilities",
      "nav.book": "Book", "nav.contact": "Contact", "nav.signin": "Sign in",
      "nav.dash": "Dashboard", "nav.patients": "Patients", "nav.doctors": "Doctors", "nav.appts": "Appointments",
      "nav.pharm": "Pharmacy", "nav.ward": "Ward Allotment", "nav.dx": "Diagnostics", "nav.pay": "Payments",
      "nav.reports": "Reports", "nav.alerts": "Email & SMS"
    },
    hi: {
      "nav.home": "होम", "nav.about": "हमारे बारे में", "nav.depts": "विभाग", "nav.facilities": "सुविधाएँ",
      "nav.book": "अपॉइंटमेंट", "nav.contact": "संपर्क", "nav.signin": "साइन इन",
      "nav.dash": "डैशबोर्ड", "nav.patients": "मरीज़", "nav.doctors": "डॉक्टर", "nav.appts": "अपॉइंटमेंट",
      "nav.pharm": "फार्मेसी", "nav.ward": "वार्ड", "nav.dx": "जांच", "nav.pay": "भुगतान",
      "nav.reports": "रिपोर्ट", "nav.alerts": "ईमेल और SMS"
    }
  };
  MC.lang = function () {
    try { return localStorage.getItem("mc_lang") || "en"; } catch (e) { return "en"; }
  };
  MC.setLang = function (l) {
    try { localStorage.setItem("mc_lang", l === "hi" ? "hi" : "en"); } catch (e) {}
  };
  MC.t = function (key, fallback) {
    var pack = MC.I18N[MC.lang()] || MC.I18N.en;
    return pack[key] || MC.I18N.en[key] || fallback || key;
  };
  window.MCApplyI18n = function () {
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      el.textContent = MC.t(el.getAttribute("data-i18n"), el.textContent);
    });
  };

  MC.NAV_PATIENTS = [
    { href: "admin-patients.html", label: "All patients" },
    { href: "patients.html", label: "Patient records" },
    { href: "appointments.html", label: "Appointments" },
    { href: "diagnostics.html", label: "Reports" },
    { href: "payment.html", label: "Bills" }
  ];

  MC.adminView = function () {
    try { return sessionStorage.getItem("mc_admin_view") || "combined"; } catch (e) { return "combined"; }
  };

  MC.setAdminView = function (view) {
    try { sessionStorage.setItem("mc_admin_view", view); } catch (e) {}
  };

  MC.navFor = function (sess) {
    if (!sess || sess.role !== "admin") return MC.NAV;
    var view = MC.adminView();
    if (view === "patients") return MC.NAV_PATIENTS;
    if (view === "combined") {
      var extra = { href: "admin-patients.html", label: "Patient portal" };
      var list = MC.NAV.slice();
      list.splice(3, 0, extra);
      return list;
    }
    return MC.NAV;
  };

  MC.toast = function (msg, kind) {
    var wrap = document.getElementById("toasts");
    if (!wrap) {
      wrap = document.createElement("div");
      wrap.id = "toasts";
      wrap.className = "toast-wrap";
      document.body.appendChild(wrap);
    }
    var el = document.createElement("div");
    el.className = "toast " + (kind || "");
    el.textContent = msg;
    wrap.appendChild(el);
    setTimeout(function () { el.remove(); }, 2800);
  };

  MC.openModal = function (id) {
    var m = document.getElementById(id);
    if (m) m.classList.add("show");
  };
  MC.closeModal = function (id) {
    var m = document.getElementById(id);
    if (m) m.classList.remove("show");
  };

  function currentPage() {
    return document.body.getAttribute("data-page") || (location.pathname.split("/").pop() || "index.html");
  }

  function brandHtml() {
    return '<a class="brand" href="index.html">' +
      '<div class="brand-mark" aria-hidden="true"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M12 5v14M5 12h14"/></svg></div>' +
      '<div><div class="brand-name">MediCore</div><div class="brand-sub">Hospital</div></div></a>';
  }

  function viewSwitchHtml(sess) {
    if (!sess || sess.role !== "admin") return "";
    var view = MC.adminView();
    function btn(id, label) {
      return '<button type="button" data-admin-view="' + id + '" class="' + (view === id ? "on" : "") + '">' + label + "</button>";
    }
    return '<div class="view-switch" role="group" aria-label="Admin view">' +
      btn("staff", "Staff") + btn("patients", "Patients") + btn("combined", "Combined") +
      "</div>";
  }

  MC.renderStaffChrome = function () {
    var page = currentPage();
    var sess = MC.refreshSessionName() || MC.session();
    if (!sess) return;
    var navItems = MC.navFor(sess);
    var sidebar = document.getElementById("sidebar");
    if (sidebar) {
      var links = navItems.map(function (n) {
        var on = n.href === page ? " active" : "";
        return '<a class="' + on.trim() + '" href="' + n.href + '"' + (on ? ' aria-current="page"' : "") + ">" + MC.t(n.key, n.label) + "</a>";
      }).join("");
      sidebar.innerHTML = brandHtml() +
        '<nav class="nav" aria-label="Hospital modules">' + links + "</nav>" +
        '<div class="sidebar-foot">Signed in as ' + MC.esc(sess.name) + "<br>" + MC.esc(sess.id) +
        (sess.role === "admin" ? " · Admin" : "") + "</div>";
    }

    var top = document.getElementById("topbar");
    var title = document.getElementById("pageTitle");
    var sub = document.getElementById("pageSub");
    var extra = document.getElementById("pageActions");
    if (top) {
      top.innerHTML =
        '<div style="display:flex;gap:12px;align-items:flex-start;">' +
          '<button class="menu-btn" type="button" aria-label="Open menu" id="menuBtn">' +
            '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg>' +
          "</button>" +
          '<div><div class="page-kicker">MediCore</div>' +
          '<h1 class="page-title">' + (title ? title.innerHTML : "") + "</h1>" +
          '<p class="page-sub">' + (sub ? sub.textContent : "") + "</p></div></div>" +
        '<div class="top-actions" id="topActions"></div>';
      var actions = document.getElementById("topActions");
      if (extra) {
        while (extra.firstChild) actions.appendChild(extra.firstChild);
      }
      actions.insertAdjacentHTML("beforeend",
        viewSwitchHtml(sess) +
        '<span class="live"><i></i> Live</span>' +
        '<div class="who"><b>' + MC.esc(sess.name) + "</b>" + MC.esc(sess.department || sess.role) + "</div>" +
        '<div class="avatar" title="' + MC.esc(sess.name) + '">' + MC.esc(MC.initials(sess.name)) + "</div>" +
        '<button class="btn btn-ghost btn-sm lang-toggle" type="button" id="langBtn">' + (MC.lang() === "hi" ? "English" : "हिन्दी") + "</button>" +
        '<button class="btn btn-ghost btn-sm" type="button" id="signOutBtn">Sign out</button>');
    }

    var overlay = document.getElementById("overlay");
    var menuBtn = document.getElementById("menuBtn");
    if (menuBtn && sidebar) menuBtn.addEventListener("click", function () {
      sidebar.classList.add("open");
      if (overlay) overlay.classList.add("show");
    });
    if (overlay && sidebar) overlay.addEventListener("click", function () {
      sidebar.classList.remove("open");
      overlay.classList.remove("show");
    });
    var out = document.getElementById("signOutBtn");
    if (out) out.addEventListener("click", function () { MC.logout(); });
    var langBtnStaff = document.getElementById("langBtn");
    if (langBtnStaff) langBtnStaff.addEventListener("click", function () {
      MC.setLang(MC.lang() === "hi" ? "en" : "hi");
      location.reload();
    });

    var PHOTOS = {
      "dashboard.html": "img/reception.jpg",
      "patients.html": "img/ward.jpg",
      "admin-patients.html": "img/ward.jpg",
      "doctors.html": "img/consult.jpg",
      "appointments.html": "img/reception.jpg",
      "pharmacy.html": "img/pharmacy.jpg",
      "ward-allotment.html": "img/ward.jpg",
      "diagnostics.html": "img/diagnostics.jpg",
      "payment.html": "img/reception.jpg",
      "reports.html": "img/diagnostics.jpg",
      "notifications.html": "img/consult.jpg",
      "index.html": "img/campus.jpg"
    };
    var content = document.querySelector(".main > .content");
    if (content && PHOTOS[page] && !content.querySelector(".console-photo")) {
      var banner = document.createElement("div");
      banner.className = "console-photo";
      banner.innerHTML = '<img src="' + PHOTOS[page] + '" alt="">';
      content.insertBefore(banner, content.firstChild);
    }

    document.querySelectorAll("[data-admin-view]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var next = btn.getAttribute("data-admin-view");
        MC.setAdminView(next);
        if (next === "patients" && page !== "admin-patients.html" && page !== "patients.html") {
          location.href = "admin-patients.html";
          return;
        }
        if (next !== "patients" && page === "admin-patients.html") {
          location.href = "dashboard.html";
          return;
        }
        location.reload();
      });
    });
  };

  function wirePublicNav() {
    var nav = document.getElementById("pubNav");
    var page = currentPage();
    if (nav) {
      var links = [
        ["index.html", "nav.home", "Home"],
        ["about.html", "nav.about", "About"],
        ["departments.html", "nav.depts", "Departments"],
        ["facilities.html", "nav.facilities", "Facilities"],
        ["book.html", "nav.book", "Book"],
        ["contact.html", "nav.contact", "Contact"]
      ];
      nav.innerHTML = links.map(function (n) {
        var on = n[0] === page ? " active" : "";
        return '<a data-nav data-i18n="' + n[1] + '" class="' + on.trim() + '" href="' + n[0] + '">' + n[2] + "</a>";
      }).join("") +
        '<button type="button" class="lang-toggle" id="langBtn">' + (MC.lang() === "hi" ? "English" : "हिन्दी") + "</button>" +
        '<a class="btn btn-primary btn-sm" data-i18n="nav.signin" href="login.html">Sign in</a>';
    }
    var btn = document.getElementById("pubMenuBtn");
    if (btn && nav) {
      btn.addEventListener("click", function () { nav.classList.toggle("open"); });
    }
    var langBtn = document.getElementById("langBtn");
    if (langBtn) langBtn.addEventListener("click", function () {
      MC.setLang(MC.lang() === "hi" ? "en" : "hi");
      location.reload();
    });
    if (window.MCApplyI18n) MCApplyI18n();
  }

  MC.fillModuleGrid = function (el) {
    if (!el) return;
    var logged = !!MC.session();
    el.innerHTML = MC.NAV.filter(function (n) { return n.href !== "index.html"; }).map(function (n) {
      var href = logged ? n.href : "login.html#staff";
      return '<a class="mod" href="' + href + '"><h3>' + n.label + '</h3><p>' +
        (logged ? "Open the " + n.label.toLowerCase() + " console" : "Staff sign in required") +
        '</p><div class="go">' + (logged ? "Open →" : "Sign in →") + "</div></a>";
    }).join("");
  };

  MC.bindLoginForm = function (formId) {
    var form = document.getElementById(formId);
    if (!form) return;
    var pending = null;
    function show(id, on) {
      var el = document.getElementById(id);
      if (el) el.style.display = on ? "" : "none";
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var box = document.getElementById("loginErr");
      var btn = document.getElementById("loginGo");
      if (pending) {
        var code = (document.getElementById("otpCode") || {}).value;
        if (btn) { btn.disabled = true; btn.textContent = "Checking…"; }
        MC.verifyOtp(pending.challenge, pending.uid, pending.role, code).then(function (res) {
          if (btn) { btn.disabled = false; btn.textContent = "Verify code"; }
          if (!res.ok) {
            if (box) { box.textContent = res.error; box.style.display = "block"; }
            return;
          }
          location.href = MC.homeFor(res.session);
        });
        return;
      }
      var id = (document.getElementById("loginId") || {}).value;
      var pw = (document.getElementById("loginPw") || {}).value;
      var role = (document.getElementById("loginRole") || {}).value || "staff";
      if (btn) { btn.disabled = true; btn.textContent = "Signing in…"; }
      MC.login(id, pw, role).then(function (res) {
        if (btn) { btn.disabled = false; btn.textContent = "Continue"; }
        if (!res.ok) {
          if (box) { box.textContent = res.error; box.style.display = "block"; }
          return;
        }
        pending = res;
        show("passFields", false);
        show("otpFields", true);
        if (btn) btn.textContent = "Verify code";
        var hint = document.getElementById("otpHint");
        if (hint) hint.textContent = "Enter the 6-digit code for " + (res.mask || "your phone");
        var demo = document.getElementById("otpDemo");
        var otp = document.getElementById("otpCode");
        if (res.demo_code) {
          if (demo) {
            demo.style.display = "block";
            demo.innerHTML = "Your OTP (demo — no SMS account): <b style='font-size:22px;letter-spacing:0.12em'>" + res.demo_code + "</b>";
          }
          if (otp) otp.value = res.demo_code;
        } else if (demo) demo.style.display = "none";
        if (otp) otp.focus();
      });
    });
  };

  document.addEventListener("DOMContentLoaded", function () {
    MC.boot().then(function () {
      var auth = document.body.getAttribute("data-auth") || "public";
      if (auth === "staff") {
        if (!MC.requireStaff()) return;
        MC.renderStaffChrome();
      } else if (auth === "patient") {
        if (!MC.requirePatient()) return;
      } else if (auth === "home") {
        var pub = document.getElementById("publicRoot");
        var staff = document.getElementById("staffRoot");
        var sess = MC.session();
        if (sess && sess.role === "patient") {
          location.href = "patient.html";
          return;
        }
        if (sess && staff) {
          if (pub) pub.style.display = "none";
          staff.style.display = "block";
          MC.renderStaffChrome();
        } else {
          if (staff) staff.style.display = "none";
          if (pub) pub.style.display = "block";
          wirePublicNav();
        }
        MC.fillModuleGrid(document.getElementById("modGridStaff"));
      } else {
        wirePublicNav();
      }
      document.querySelectorAll(".modal-back").forEach(function (el) {
        el.addEventListener("click", function (e) {
          if (e.target === el) el.classList.remove("show");
        });
      });
      if (!MC._online && (auth === "staff" || auth === "patient")) {
        MC.toast("Hospital server is waking up. Open http://127.0.0.1:5000 in a moment.", "bad");
      }
    });
  });
})(window);
