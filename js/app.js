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
      "nav.book": "Book", "nav.contact": "Contact", "nav.signin": "Sign in", "nav.signout": "Sign out",
      "nav.dash": "Dashboard", "nav.patients": "Patients", "nav.doctors": "Doctors", "nav.appts": "Appointments",
      "nav.pharm": "Pharmacy", "nav.ward": "Ward Allotment", "nav.dx": "Diagnostics", "nav.pay": "Payments",
      "nav.reports": "Reports", "nav.alerts": "Email & SMS",
      "ui.live": "Live", "ui.admin": "Admin", "ui.staff": "Staff", "ui.patients": "Patients",
      "home.kicker": "Mumbai · Open 24×7",
      "home.h1": "Care for your family, every hour of the day.",
      "home.lead": "From the emergency porch to maternity and children’s wards, MediCore is a city hospital for when you need a doctor, a bed, or a quiet word of reassurance.",
      "home.patient": "Patient login", "home.staff": "Staff / Admin", "home.visit": "Emergency & visiting",
      "home.beds": "Beds on campus", "home.docs": "Specialist doctors", "home.er": "Emergency & ambulance",
      "login.title": "Sign in", "login.continue": "Continue", "login.forgot": "Forgot password",
      "login.staff": "Staff", "login.patient": "Patient", "login.admin": "Admin",
      "login.staffHint": "Wards, pharmacy, billing", "login.patientHint": "Your reports and bills", "login.adminHint": "Whole hospital",
      "login.idStaff": "Staff ID", "login.idPatient": "Patient ID", "login.idAdmin": "Admin ID",
      "login.pw": "Password", "login.askAdmin": "Ask the hospital administrator to reset your password. For privacy we do not show sample IDs here.",
      "book.h1": "Book a slot without signing in.", "book.send": "Send request",
      "contact.h1": "Reception first. The ward second.",
      "about.h1": "A city hospital built around patients and the people who look after them.",
      "dept.h1": "Eight departments, one campus.",
      "fac.h1": "Beds, labs, pharmacy and a porch that never locks."
    },
    hi: {
      "nav.home": "होम", "nav.about": "हमारे बारे में", "nav.depts": "विभाग", "nav.facilities": "सुविधाएँ",
      "nav.book": "अपॉइंटमेंट", "nav.contact": "संपर्क", "nav.signin": "साइन इन", "nav.signout": "साइन आउट",
      "nav.dash": "डैशबोर्ड", "nav.patients": "मरीज़", "nav.doctors": "डॉक्टर", "nav.appts": "अपॉइंटमेंट",
      "nav.pharm": "फार्मेसी", "nav.ward": "वार्ड", "nav.dx": "जांच", "nav.pay": "भुगतान",
      "nav.reports": "रिपोर्ट", "nav.alerts": "ईमेल और SMS",
      "ui.live": "लाइव", "ui.admin": "एडमिन", "ui.staff": "स्टाफ", "ui.patients": "मरीज़",
      "home.kicker": "मुंबई · 24×7 खुला",
      "home.h1": "आपके परिवार की देखभाल, दिन-रात।",
      "home.lead": "इमरजेंसी से मैटर्निटी और बच्चों के वार्ड तक — डॉक्टर, बिस्तर या सहारे के लिए मेडीकोर यहाँ है।",
      "home.patient": "मरीज़ लॉगिन", "home.staff": "स्टाफ / एडमिन", "home.visit": "इमरजेंसी और मुलाकात",
      "home.beds": "कैंपस पर बिस्तर", "home.docs": "विशेषज्ञ डॉक्टर", "home.er": "इमरजेंसी और एम्बुलेंस",
      "login.title": "साइन इन", "login.continue": "आगे बढ़ें", "login.forgot": "पासवर्ड भूल गए",
      "login.staff": "स्टाफ", "login.patient": "मरीज़", "login.admin": "एडमिन",
      "login.staffHint": "वार्ड, फार्मेसी, बिलिंग", "login.patientHint": "आपकी रिपोर्ट और बिल", "login.adminHint": "पूरा अस्पताल",
      "login.idStaff": "स्टाफ आईडी", "login.idPatient": "मरीज़ आईडी", "login.idAdmin": "एडमिन आईडी",
      "login.pw": "पासवर्ड", "login.askAdmin": "पासवर्ड रीसेट के लिए अस्पताल प्रशासक से कहें। गोपनीयता के लिए यहाँ नमूना आईडी नहीं दिखते।",
      "book.h1": "बिना साइन इन स्लॉट बुक करें।", "book.send": "अनुरोध भेजें",
      "contact.h1": "पहले रिसेप्शन। फिर वार्ड।",
      "about.h1": "मरीज़ों और देखभाल करने वालों के लिए बना शहर का अस्पताल।",
      "dept.h1": "आठ विभाग, एक कैंपस।",
      "fac.h1": "बिस्तर, लैब, फार्मेसी — और एक पोर्च जो बंद नहीं होता।"
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
  MC.HI_PLAIN = {
    "Home": "होम", "About": "हमारे बारे में", "Departments": "विभाग", "Facilities": "सुविधाएँ",
    "Book": "अपॉइंटमेंट", "Contact": "संपर्क", "Sign in": "साइन इन", "Sign out": "साइन आउट",
    "Dashboard": "डैशबोर्ड", "Patients": "मरीज़", "Doctors": "डॉक्टर", "Appointments": "अपॉइंटमेंट",
    "Pharmacy": "फार्मेसी", "Ward Allotment": "वार्ड", "Diagnostics": "जांच", "Payments": "भुगतान",
    "Reports": "रिपोर्ट", "Email & SMS": "ईमेल और SMS", "Live": "लाइव", "Admin": "एडमिन", "Staff": "स्टाफ",
    "Patient": "मरीज़", "Continue": "आगे बढ़ें", "Password": "पासवर्ड", "Forgot password": "पासवर्ड भूल गए",
    "Mark done": "पूर्ण करें", "Undo / re-schedule": "पूर्ववत / फिर शेड्यूल", "Cancel": "रद्द",
    "Book slot": "स्लॉट बुक करें", "Send / log": "भेजें / लॉग", "Queue a message": "संदेश भेजें",
    "Schedule a scan": "स्कैन शेड्यूल", "Register patient": "मरीज़ जोड़ें", "Add doctor": "डॉक्टर जोड़ें",
    "Search": "खोज", "All": "सभी", "Scheduled": "निर्धारित", "Done": "पूर्ण", "Cancelled": "रद्द",
    "Admitted": "भर्ती", "Discharged": "डिस्चार्ज", "Observation": "निगरानी",
    "Confirmed": "पुष्टि", "Pending": "लंबित", "Checked-in": "चेक-इन",
    "Paid": "भुगतान", "Due": "बकाया", "Processing": "प्रक्रिया में",
    "Available": "उपलब्ध", "Occupied": "भरा", "Patient login": "मरीज़ लॉगिन",
    "Staff / Admin": "स्टाफ / एडमिन", "Emergency & visiting": "इमरजेंसी और मुलाकात",
    "Beds on campus": "कैंपस पर बिस्तर", "Specialist doctors": "विशेषज्ञ डॉक्टर",
    "Emergency & ambulance": "इमरजेंसी और एम्बुलेंस",
    "Care for your family, every hour of the day.": "आपके परिवार की देखभाल, दिन-रात।",
    "A hospital that still feels human.": "एक अस्पताल जो इंसानियत के साथ है।",
    "Life on campus": "कैंपस की ज़िंदगी", "When to come in": "कब आएँ",
    "Our story": "हमारी कहानी", "What we believe": "हम क्या मानते हैं", "On the floor": "वार्ड में",
    "Eight departments, one campus.": "आठ विभाग, एक कैंपस।",
    "Emergency & Trauma": "इमरजेंसी और ट्रॉमा", "Cardiology": "कार्डियोलॉजी",
    "Maternity": "मैटर्निटी", "Paediatrics": "बाल रोग", "Orthopaedics": "हड्डी रोग",
    "Oncology": "कैंसर विभाग", "Neurology": "न्यूरोलॉजी",
    "Send request": "अनुरोध भेजें", "Full name": "पूरा नाम", "Mobile": "मोबाइल",
    "Department": "विभाग", "Date": "तारीख", "Time": "समय",
    "My details": "मेरी जानकारी", "Bills": "बिल", "Pay now": "अभी भुगतान",
    "Open dashboard": "डैशबोर्ड खोलें", "Good to have you on the floor.": "वार्ड में आपका स्वागत है।",
    "Show": "दिखाएँ", "Hide": "छिपाएँ", "Menu": "मेनू"
  };
  window.MCApplyI18n = function () {
    document.documentElement.lang = MC.lang() === "hi" ? "hi" : "en";
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      el.textContent = MC.t(el.getAttribute("data-i18n"), el.textContent);
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
      el.setAttribute("placeholder", MC.t(el.getAttribute("data-i18n-placeholder"), el.getAttribute("placeholder") || ""));
    });
    if (MC.lang() !== "hi") return;
    function walk(node) {
      if (!node) return;
      if (node.nodeType === 3) {
        var raw = node.nodeValue;
        var t = raw.replace(/^\s+|\s+$/g, "");
        if (t && MC.HI_PLAIN[t]) node.nodeValue = raw.replace(t, MC.HI_PLAIN[t]);
        return;
      }
      if (node.nodeType !== 1) return;
      var tag = node.tagName;
      if (tag === "SCRIPT" || tag === "STYLE" || tag === "CODE" || tag === "INPUT" || tag === "TEXTAREA") return;
      if (node.getAttribute && node.getAttribute("data-i18n")) {
        Array.prototype.forEach.call(node.childNodes, walk);
        return;
      }
      Array.prototype.forEach.call(node.childNodes, walk);
    }
    walk(document.body);
    document.querySelectorAll("option").forEach(function (opt) {
      if (MC.HI_PLAIN[opt.text]) opt.text = MC.HI_PLAIN[opt.text];
    });
    document.querySelectorAll("button, label, th, h1, h2, h3, .page-title, .page-sub, .kicker, .lead").forEach(function (el) {
      var t = (el.textContent || "").replace(/^\s+|\s+$/g, "");
      if (MC.HI_PLAIN[t] && el.children.length === 0) el.textContent = MC.HI_PLAIN[t];
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
      '<img class="brand-logo" src="img/logo-LIVE.jpg" width="36" height="36" alt="MediCore">' +
      '<div><div class="brand-name">MediCore</div><div class="brand-sub">Hospital</div></div></a>';
  }

  function viewSwitchHtml(sess) {
    if (!sess || sess.role !== "admin") return "";
    var view = MC.adminView();
    function btn(id, label) {
      return '<button type="button" data-admin-view="' + id + '" class="' + (view === id ? "on" : "") + '">' + label + "</button>";
    }
    return '<div class="view-switch" role="group" aria-label="Admin view">' +
      btn("staff", MC.t("ui.staff", "Staff")) + btn("patients", MC.t("ui.patients", "Patients")) + btn("combined", MC.t("ui.admin", "Admin")) +
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
        '<div class="sidebar-foot">' + MC.t("Signed in as ", "Signed in as ") + MC.esc(sess.name) + "<br>" + MC.esc(sess.id) +
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
        '<span class="live"><i></i> ' + MC.t("ui.live", "Live") + "</span>" +
        '<div class="who"><b>' + MC.esc(sess.name) + "</b>" + MC.esc(sess.department || sess.role) + "</div>" +
        '<div class="avatar" title="' + MC.esc(sess.name) + '">' + MC.esc(MC.initials(sess.name)) + "</div>" +
        '<button class="btn btn-ghost btn-sm lang-toggle" type="button" id="langBtn">' + (MC.lang() === "hi" ? "English" : "हिन्दी") + "</button>" +
        '<button class="btn btn-ghost btn-sm" type="button" id="signOutBtn">' + MC.t("nav.signout", "Sign out") + "</button>");
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
    var sess = MC.session();
    if (nav) {
      var links = [
        ["index.html", "nav.home", "Home"],
        ["about.html", "nav.about", "About"],
        ["departments.html", "nav.depts", "Departments"],
        ["facilities.html", "nav.facilities", "Facilities"],
        ["book.html", "nav.book", "Book"],
        ["contact.html", "nav.contact", "Contact"]
      ];
      var extra;
      if (sess) {
        var consoleHref = sess.role === "patient" ? "patient.html" : "dashboard.html";
        var consoleLabel = sess.role === "patient" ? "My file" : "Dashboard";
        extra =
          '<a class="btn btn-ghost btn-sm" href="' + consoleHref + '">' + consoleLabel + "</a>" +
          '<button type="button" class="btn btn-primary btn-sm" id="pubSignOut">' + MC.t("nav.signout", "Sign out") + "</button>";
      } else {
        extra = '<a class="btn btn-primary btn-sm" data-i18n="nav.signin" href="login.html">Sign in</a>';
      }
      nav.innerHTML = links.map(function (n) {
        var on = n[0] === page ? " active" : "";
        return '<a data-nav data-i18n="' + n[1] + '" class="' + on.trim() + '" href="' + n[0] + '">' + n[2] + "</a>";
      }).join("") +
        '<button type="button" class="lang-toggle" id="langBtn">' + (MC.lang() === "hi" ? "English" : "हिन्दी") + "</button>" +
        extra;
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
    var out = document.getElementById("pubSignOut");
    if (out) out.addEventListener("click", function () { MC.logout(); });
    if (sess) {
      var patientBtn = document.querySelector('[data-i18n="home.patient"]');
      var staffBtn = document.querySelector('[data-i18n="home.staff"]');
      if (sess.role === "patient") {
        if (patientBtn) { patientBtn.setAttribute("href", "patient.html"); patientBtn.textContent = "My file"; }
        if (staffBtn) staffBtn.style.display = "none";
      } else {
        if (patientBtn) { patientBtn.setAttribute("href", "dashboard.html"); patientBtn.textContent = "Dashboard"; }
        if (staffBtn) staffBtn.style.display = "none";
      }
    }
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
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var box = document.getElementById("loginErr");
      var btn = document.getElementById("loginGo");
      var id = (document.getElementById("loginId") || {}).value;
      var pw = (document.getElementById("loginPw") || {}).value;
      var role = (document.getElementById("loginRole") || {}).value || "staff";
      if (btn) { btn.disabled = true; btn.textContent = MC.t("login.continue", "Continue"); }
      MC.login(id, pw, role).then(function (res) {
        if (btn) { btn.disabled = false; btn.textContent = MC.t("login.continue", "Continue"); }
        if (!res.ok) {
          if (box) { box.textContent = res.error; box.style.display = "block"; }
          return;
        }
        location.href = MC.homeFor(res.session);
      });
    });
  };

  document.addEventListener("DOMContentLoaded", function () {
    if (!document.querySelector('link[rel="icon"]')) {
      var icon = document.createElement("link");
      icon.rel = "icon";
      icon.type = "image/png";
      icon.href = "img/favicon.png";
      document.head.appendChild(icon);
      var apple = document.createElement("link");
      apple.rel = "apple-touch-icon";
      apple.href = "img/apple-touch-icon.png";
      document.head.appendChild(apple);
    }
    document.querySelectorAll(".brand-mark").forEach(function (el) {
      var img = document.createElement("img");
      img.className = "brand-logo";
      img.src = "img/logo-LIVE.jpg";
      img.alt = "MediCore";
      img.width = 36;
      img.height = 36;
      el.replaceWith(img);
    });
    MC.boot().then(function () {
      var auth = document.body.getAttribute("data-auth") || "public";
      if (auth === "staff") {
        if (!MC.requireStaff()) return;
        MC.renderStaffChrome();
        if (window.MCApplyI18n) MCApplyI18n();
        setTimeout(function () { if (window.MCApplyI18n) MCApplyI18n(); }, 350);
      } else if (auth === "patient") {
        if (!MC.requirePatient()) return;
      } else {
        var pub = document.getElementById("publicRoot");
        var staffRoot = document.getElementById("staffRoot");
        if (staffRoot) staffRoot.style.display = "none";
        if (pub) pub.style.display = "block";
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
