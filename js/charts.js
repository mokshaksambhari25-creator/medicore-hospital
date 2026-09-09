/* ===== Live canvas pies — redraw whenever hospital data changes ===== */
(function (w) {
  "use strict";
  var MC = w.MC || (w.MC = {});
  var PALETTE = ["#0F766E", "#B45309", "#1D4ED8", "#BE123C", "#047857", "#7C3AED", "#0E7490", "#A16207", "#334155", "#C2410C"];

  function sum(slices) {
    return slices.reduce(function (a, s) { return a + Math.max(0, Number(s.value) || 0); }, 0);
  }

  MC.pieColors = PALETTE;

  MC.drawPie = function (canvas, slices) {
    if (!canvas) return;
    var dpr = window.devicePixelRatio || 1;
    var css = canvas.clientWidth || 220;
    canvas.width = css * dpr;
    canvas.height = css * dpr;
    var ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var cx = css / 2;
    var cy = css / 2;
    var r = css / 2 - 8;
    var total = sum(slices);
    ctx.clearRect(0, 0, css, css);
    if (!total) {
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fillStyle = "#EDE7DC";
      ctx.fill();
      ctx.beginPath();
      ctx.arc(cx, cy, r * 0.55, 0, Math.PI * 2);
      ctx.fillStyle = "#fff";
      ctx.fill();
      return;
    }
    var angle = -Math.PI / 2;
    slices.forEach(function (s, i) {
      var v = Math.max(0, Number(s.value) || 0);
      if (!v) return;
      var slice = v / total * Math.PI * 2;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, r, angle, angle + slice);
      ctx.closePath();
      ctx.fillStyle = s.color || PALETTE[i % PALETTE.length];
      ctx.fill();
      angle += slice;
    });
    ctx.beginPath();
    ctx.arc(cx, cy, r * 0.55, 0, Math.PI * 2);
    ctx.fillStyle = "#fff";
    ctx.fill();
  };

  MC.mountPie = function (host, slices, title) {
    if (!host) return;
    var total = sum(slices);
    var rows = slices.filter(function (s) { return Number(s.value) > 0; });
    host.innerHTML =
      (title ? "<h3 class='pie-title'>" + MC.esc(MC.t(title, title)) + "</h3>" : "") +
      '<div class="pie-body">' +
        '<canvas class="pie-canvas" width="220" height="220"></canvas>' +
        '<ul class="pie-legend">' +
          (rows.length ? rows.map(function (s, i) {
            var v = Number(s.value) || 0;
            var pct = total ? Math.round(v / total * 100) : 0;
            var color = s.color || PALETTE[i % PALETTE.length];
            var meta = s.meta ? " · " + s.meta : "";
            return "<li><i style='background:" + color + "'></i><span>" + MC.esc(MC.t(s.label, s.label)) +
              "</span><b>" + MC.esc(s.display != null ? s.display : String(v)) + " · " + pct + "%</b>" +
              (meta ? "<em>" + MC.esc(meta) + "</em>" : "") + "</li>";
          }).join("") : "<li class='empty'>" + MC.esc(MC.t("No data yet.", "No data yet.")) + "</li>") +
        "</ul></div>";
    MC.drawPie(host.querySelector("canvas"), slices);
  };
})(window);
