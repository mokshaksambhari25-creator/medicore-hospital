/* Interactive donut + bar graph — live hospital data, hover %, click legend */
(function (w) {
  "use strict";
  var MC = w.MC || (w.MC = {});
  var PALETTE = ["#0F766E", "#B45309", "#1D4ED8", "#BE123C", "#047857", "#7C3AED", "#0E7490", "#A16207", "#334155", "#C2410C"];
  MC.pieColors = PALETTE;

  function sum(slices) {
    return slices.reduce(function (a, s) { return a + Math.max(0, Number(s.value) || 0); }, 0);
  }
  function color(s, i) { return s.color || PALETTE[i % PALETTE.length]; }
  function ease(t) { return 1 - Math.pow(1 - t, 3); }

  function layout(slices) {
    var total = sum(slices) || 1;
    var angle = -Math.PI / 2;
    return slices.map(function (s, i) {
      var v = Math.max(0, Number(s.value) || 0);
      var sweep = v / total * Math.PI * 2;
      var row = {
        i: i, label: s.label, value: v, display: s.display, meta: s.meta,
        color: color(s, i), pct: total ? (v / total * 100) : 0,
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
      var s = rows[i].start, e = rows[i].end;
      if (a >= s && a < e) return i;
    }
    return -1;
  }

  function drawDonut(ctx, rows, css, hover, progress) {
    var cx = css / 2, cy = css / 2;
    var r = css / 2 - 18;
    var inner = r * 0.58;
    ctx.clearRect(0, 0, css, css);
    ctx.save();
    ctx.shadowColor = "rgba(18,60,56,0.18)";
    ctx.shadowBlur = 12;
    ctx.shadowOffsetY = 4;
    rows.forEach(function (row) {
      if (row.value <= 0) return;
      var start = -Math.PI / 2 + (row.start + Math.PI / 2) * progress;
      var end = -Math.PI / 2 + (row.end + Math.PI / 2) * progress;
      var explode = (hover === row.i) ? 7 : 0;
      var mx = Math.cos(row.mid) * explode;
      var my = Math.sin(row.mid) * explode;
      ctx.beginPath();
      ctx.moveTo(cx + mx, cy + my);
      ctx.arc(cx + mx, cy + my, r, start, end);
      ctx.arc(cx + mx, cy + my, inner, end, start, true);
      ctx.closePath();
      ctx.globalAlpha = hover >= 0 && hover !== row.i ? 0.38 : 1;
      ctx.fillStyle = row.color;
      ctx.fill();
      ctx.globalAlpha = 1;
    });
    ctx.restore();
    if (progress < 0.95) return;
    ctx.font = "700 11px Inter, system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    rows.forEach(function (row) {
      if (row.pct < 8) return;
      var rr = (r + inner) / 2;
      ctx.fillStyle = "#fff";
      ctx.fillText(Math.round(row.pct) + "%", cx + Math.cos(row.mid) * rr, cy + Math.sin(row.mid) * rr);
    });
  }

  MC.mountPie = function (host, slices, title) {
    MC.mountChart(host, slices, { title: title });
  };

  MC.mountChart = function (host, slices, opts) {
    if (!host) return;
    opts = opts || {};
    var sig = JSON.stringify((slices || []).map(function (s) { return [s.label, s.value, s.display]; }));
    if (host.getAttribute("data-sig") === sig && host.querySelector("canvas")) return;
    host.setAttribute("data-sig", sig);
    var title = opts.title || "";
    var center = opts.center || "";
    var rows0 = (slices || []).filter(function (s) { return Number(s.value) > 0; });
    var total = sum(slices || []);
    var fmtTotal = opts.totalDisplay != null ? opts.totalDisplay : (total ? String(total) : "0");

    host.innerHTML =
      (title ? "<h3 class='pie-title'>" + MC.esc(MC.t(title, title)) + "</h3>" : "") +
      '<div class="chart-pair">' +
        '<div class="pie-stage">' +
          '<canvas class="pie-canvas" width="240" height="240"></canvas>' +
          '<div class="pie-center"><b></b><span></span></div>' +
          '<div class="pie-tip" hidden></div>' +
        "</div>" +
        '<div class="bar-col"></div>' +
      "</div>" +
      '<ul class="pie-legend"></ul>';

    var canvas = host.querySelector("canvas");
    var tip = host.querySelector(".pie-tip");
    var centerEl = host.querySelector(".pie-center");
    var barCol = host.querySelector(".bar-col");
    var legend = host.querySelector(".pie-legend");
    var hover = -1;
    var rows = layout(slices || []);
    var live = rows.filter(function (r) { return r.value > 0; });

    centerEl.querySelector("b").textContent = fmtTotal;
    centerEl.querySelector("span").textContent = MC.t(center || "Total", center || "Total");

    barCol.innerHTML = live.length ? live.map(function (r) {
      return '<div class="g-bar" data-i="' + r.i + '">' +
        '<div class="g-bar-top"><span>' + MC.esc(MC.t(r.label, r.label)) + "</span><b>" +
        MC.esc(r.display != null ? r.display : String(r.value)) + " · " + Math.round(r.pct) + "%</b></div>" +
        '<div class="g-track"><i style="width:0;background:' + r.color + '"></i></div></div>';
    }).join("") : '<p class="empty">' + MC.esc(MC.t("No data yet.", "No data yet.")) + "</p>";

    legend.innerHTML = live.length ? live.map(function (r) {
      return '<li data-i="' + r.i + '"><i style="background:' + r.color + '"></i><span>' +
        MC.esc(MC.t(r.label, r.label)) + "</span><b>" + Math.round(r.pct) + "%</b></li>";
    }).join("") : "";

    var css = 240;
    var dpr = window.devicePixelRatio || 1;
    canvas.width = css * dpr;
    canvas.height = css * dpr;
    canvas.style.width = css + "px";
    canvas.style.height = css + "px";
    var ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    var start = performance.now();
    function frame(now) {
      var p = ease(Math.min(1, (now - start) / 700));
      drawDonut(ctx, rows, css, hover, p);
      if (p < 1) requestAnimationFrame(frame);
      else {
        [].forEach.call(barCol.querySelectorAll(".g-track i"), function (el, idx) {
          var r = live[idx];
          if (r) el.style.width = r.pct + "%";
        });
      }
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
      tip.innerHTML = "<strong>" + MC.esc(MC.t(r.label, r.label)) + "</strong>" +
        "<span>" + MC.esc(r.display != null ? r.display : String(r.value)) + "</span>" +
        "<b>" + (Math.round(r.pct * 10) / 10) + "%</b>";
      if (ev && canvas) {
        var box = canvas.getBoundingClientRect();
        tip.style.left = Math.min(box.width - 8, Math.max(8, ev.clientX - box.left)) + "px";
        tip.style.top = Math.max(8, ev.clientY - box.top - 8) + "px";
      }
    }

    canvas.onmousemove = function (ev) {
      var box = canvas.getBoundingClientRect();
      var x = (ev.clientX - box.left) * (css / box.width);
      var y = (ev.clientY - box.top) * (css / box.height);
      setHover(hit(rows, css / 2, css / 2, x, y, (css / 2 - 18) * 0.58, css / 2 - 18), ev);
    };
    canvas.onmouseleave = function () { setHover(-1); };
    host.onclick = function (ev) {
      var el = ev.target.closest("[data-i]");
      if (!el) return;
      var i = Number(el.getAttribute("data-i"));
      setHover(hover === i ? -1 : i, ev);
    };
  };
})(window);
