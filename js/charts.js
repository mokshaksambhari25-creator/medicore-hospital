/* Pie OR bar graph — never both in the same card */
(function (w) {
  "use strict";
  var MC = w.MC || (w.MC = {});
  var PALETTE = ["#0F766E", "#B45309", "#1D4ED8", "#BE123C", "#047857", "#7C3AED", "#0E7490", "#A16207"];
  MC.pieColors = PALETTE;

  function sum(slices) {
    return slices.reduce(function (a, s) { return a + Math.max(0, Number(s.value) || 0); }, 0);
  }
  function color(s, i) { return s.color || PALETTE[i % PALETTE.length]; }
  function ease(t) { return 1 - Math.pow(1 - t, 3); }
  function same(host, slices, kind) {
    var sig = kind + ":" + JSON.stringify((slices || []).map(function (s) { return [s.label, s.value, s.display]; }));
    if (host.getAttribute("data-sig") === sig && host.querySelector(".pie-stage, .h-chart, .col-chart")) return true;
    host.setAttribute("data-sig", sig);
    return false;
  }
  function layout(slices) {
    var total = sum(slices) || 1;
    var angle = -Math.PI / 2;
    return slices.map(function (s, i) {
      var v = Math.max(0, Number(s.value) || 0);
      var sweep = v / total * Math.PI * 2;
      var row = {
        i: i, label: s.label, value: v, display: s.display,
        color: color(s, i), pct: v / total * 100,
        start: angle, end: angle + sweep, mid: angle + sweep / 2
      };
      angle += sweep;
      return row;
    });
  }
  function hit(rows, cx, cy, x, y, rInner, rOuter) {
    var dx = x - cx, dy = y - cy;
    var dist = Math.sqrt(dx * dx + dy * dy);
    if (dist < rInner || dist > rOuter + 8) return -1;
    var a = Math.atan2(dy, dx);
    if (a < -Math.PI / 2) a += Math.PI * 2;
    for (var i = 0; i < rows.length; i++) {
      if (rows[i].value <= 0) continue;
      if (a >= rows[i].start && a < rows[i].end) return i;
    }
    return -1;
  }
  function drawDonut(ctx, rows, css, hover, progress) {
    var cx = css / 2, cy = css / 2, r = css / 2 - 16, inner = r * 0.56;
    ctx.clearRect(0, 0, css, css);
    ctx.save();
    ctx.shadowColor = "rgba(18,60,56,0.2)";
    ctx.shadowBlur = 14;
    ctx.shadowOffsetY = 5;
    rows.forEach(function (row) {
      if (row.value <= 0) return;
      var start = -Math.PI / 2 + (row.start + Math.PI / 2) * progress;
      var end = -Math.PI / 2 + (row.end + Math.PI / 2) * progress;
      var ex = hover === row.i ? 8 : 0;
      var mx = Math.cos(row.mid) * ex, my = Math.sin(row.mid) * ex;
      ctx.globalAlpha = hover >= 0 && hover !== row.i ? 0.35 : 1;
      ctx.beginPath();
      ctx.moveTo(cx + mx, cy + my);
      ctx.arc(cx + mx, cy + my, r, start, end);
      ctx.arc(cx + mx, cy + my, inner, end, start, true);
      ctx.closePath();
      ctx.fillStyle = row.color;
      ctx.fill();
      ctx.globalAlpha = 1;
    });
    ctx.restore();
    if (progress < 0.92) return;
    ctx.font = "700 12px Inter, system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = "#fff";
    rows.forEach(function (row) {
      if (row.pct < 7) return;
      var rr = (r + inner) / 2;
      ctx.fillText(Math.round(row.pct) + "%", cx + Math.cos(row.mid) * rr, cy + Math.sin(row.mid) * rr);
    });
  }

  MC.mountPie = function (host, slices, opts) {
    if (!host) return;
    opts = opts || {};
    if (typeof opts === "string") opts = { title: opts };
    if (same(host, slices, "pie")) return;
    var title = opts.title || "";
    var rows = layout(slices || []);
    var live = rows.filter(function (r) { return r.value > 0; });
    var total = sum(slices || []);
    var fmtTotal = opts.totalDisplay != null ? opts.totalDisplay : String(total);
    host.innerHTML =
      (title ? "<h3 class='pie-title'>" + MC.esc(MC.t(title, title)) + "</h3>" : "") +
      '<div class="pie-stage">' +
        '<canvas class="pie-canvas" width="240" height="240"></canvas>' +
        '<div class="pie-center"><b>' + MC.esc(fmtTotal) + "</b><span>" + MC.esc(MC.t(opts.center || "Total", opts.center || "Total")) + "</span></div>" +
        '<div class="pie-tip" hidden></div>' +
      "</div>" +
      '<ul class="pie-legend">' +
        live.map(function (r) {
          return '<li data-i="' + r.i + '"><i style="background:' + r.color + '"></i><span>' +
            MC.esc(MC.t(r.label, r.label)) + "</span><b>" + Math.round(r.pct) + "%</b></li>";
        }).join("") +
      "</ul>";
    var canvas = host.querySelector("canvas");
    var tip = host.querySelector(".pie-tip");
    var hover = -1;
    var css = 240;
    var dpr = window.devicePixelRatio || 1;
    canvas.width = css * dpr;
    canvas.height = css * dpr;
    var ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var t0 = performance.now();
    function frame(now) {
      var p = ease(Math.min(1, (now - t0) / 800));
      drawDonut(ctx, rows, css, hover, p);
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
    function setHover(i, ev) {
      hover = i;
      drawDonut(ctx, rows, css, hover, 1);
      [].forEach.call(host.querySelectorAll("[data-i]"), function (el) {
        el.classList.toggle("on", Number(el.getAttribute("data-i")) === i);
        el.classList.toggle("dim", i >= 0 && Number(el.getAttribute("data-i")) !== i);
      });
      if (i < 0 || !rows[i]) { tip.hidden = true; return; }
      var r = rows[i];
      tip.hidden = false;
      tip.innerHTML = "<strong>" + MC.esc(MC.t(r.label, r.label)) + "</strong><span>" +
        MC.esc(r.display != null ? r.display : String(r.value)) + "</span><b>" + (Math.round(r.pct * 10) / 10) + "%</b>";
      if (ev) {
        var box = canvas.getBoundingClientRect();
        tip.style.left = Math.min(box.width - 8, Math.max(8, ev.clientX - box.left)) + "px";
        tip.style.top = Math.max(8, ev.clientY - box.top - 8) + "px";
      }
    }
    canvas.onmousemove = function (ev) {
      var box = canvas.getBoundingClientRect();
      setHover(hit(rows, css / 2, css / 2, (ev.clientX - box.left) * (css / box.width), (ev.clientY - box.top) * (css / box.height), (css / 2 - 16) * 0.56, css / 2 - 16), ev);
    };
    canvas.onmouseleave = function () { setHover(-1); };
    host.onclick = function (ev) {
      var el = ev.target.closest("[data-i]");
      if (!el) return;
      var i = Number(el.getAttribute("data-i"));
      setHover(hover === i ? -1 : i, ev);
    };
  };

  MC.mountBars = function (host, slices, opts) {
    if (!host) return;
    opts = opts || {};
    if (typeof opts === "string") opts = { title: opts };
    if (same(host, slices, "hbar")) return;
    var title = opts.title || "";
    var rows = layout(slices || []).filter(function (r) { return r.value > 0; });
    var maxV = rows.reduce(function (a, r) { return Math.max(a, r.value); }, 0) || 1;
    host.innerHTML =
      (title ? "<h3 class='pie-title'>" + MC.esc(MC.t(title, title)) + "</h3>" : "") +
      '<div class="h-chart">' +
        (rows.length ? rows.map(function (r) {
          var w = Math.max(4, (r.value / maxV) * 100);
          return '<div class="h-row" data-i="' + r.i + '" title="' + MC.esc(r.label) + '">' +
            '<div class="h-label">' + MC.esc(MC.t(r.label, r.label)) + "</div>" +
            '<div class="h-track"><i style="width:0;background:' + r.color + '" data-w="' + w + '"></i></div>' +
            '<div class="h-meta"><b>' + MC.esc(r.display != null ? r.display : String(r.value)) + "</b>" +
            "<span>" + Math.round(r.pct) + "%</span></div></div>";
        }).join("") : '<p class="empty">' + MC.esc(MC.t("No data yet.", "No data yet.")) + "</p>") +
      "</div>";
    requestAnimationFrame(function () {
      [].forEach.call(host.querySelectorAll(".h-track i"), function (el, idx) {
        setTimeout(function () { el.style.width = el.getAttribute("data-w") + "%"; }, 50 + idx * 70);
      });
    });
  };

  MC.mountChart = MC.mountPie;
})(window);
