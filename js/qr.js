/* Compact QR (byte mode, versions 1–10) — UPI / invoice payloads */
(function (w) {
  "use strict";
  var MC = w.MC || (w.MC = {});

  var EXP = new Array(512);
  var LOG = new Array(256);
  (function () {
    var x = 1;
    for (var i = 0; i < 255; i++) {
      EXP[i] = x;
      LOG[x] = i;
      x <<= 1;
      if (x & 256) x ^= 0x11d;
    }
    for (i = 255; i < 512; i++) EXP[i] = EXP[i - 255];
  })();
  function mul(a, b) { return a && b ? EXP[LOG[a] + LOG[b]] : 0; }

  var ECC = {
    1: [19, 7, 1], 2: [34, 10, 1], 3: [55, 15, 1], 4: [80, 20, 1],
    5: [108, 26, 1], 6: [136, 18, 2], 7: [156, 20, 2], 8: [194, 24, 2],
    9: [232, 30, 2], 10: [274, 18, 4]
  };
  var ALIGN = {
    2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30], 6: [6, 34],
    7: [6, 22, 38], 8: [6, 24, 42], 9: [6, 26, 46], 10: [6, 28, 50]
  };

  function rsPoly(n) {
    var poly = [1];
    for (var i = 0; i < n; i++) {
      var next = new Array(poly.length + 1);
      for (var j = 0; j < next.length; j++) next[j] = 0;
      for (j = 0; j < poly.length; j++) {
        next[j] ^= poly[j];
        next[j + 1] ^= mul(poly[j], EXP[i]);
      }
      poly = next;
    }
    return poly;
  }
  function rs(data, n) {
    var poly = rsPoly(n);
    var ecc = new Array(n);
    for (var i = 0; i < n; i++) ecc[i] = 0;
    for (i = 0; i < data.length; i++) {
      var f = data[i] ^ ecc[0];
      ecc.shift();
      ecc.push(0);
      if (!f) continue;
      for (var j = 0; j < n; j++) ecc[j] ^= mul(poly[j + 1], f);
    }
    return ecc;
  }

  function bitsToBytes(bits) {
    var out = [];
    for (var i = 0; i < bits.length; i += 8) {
      var v = 0;
      for (var j = 0; j < 8; j++) v = (v << 1) | (bits[i + j] || 0);
      out.push(v);
    }
    return out;
  }

  function encode(text, ver) {
    var bytes = [];
    for (var i = 0; i < text.length; i++) bytes.push(text.charCodeAt(i) & 255);
    var spec = ECC[ver];
    var dataCount = spec[0];
    var eccLen = spec[1];
    var blocks = spec[2];
    var bits = [];
    function push(val, len) {
      for (var i = len - 1; i >= 0; i--) bits.push((val >> i) & 1);
    }
    push(4, 4);
    push(bytes.length, ver < 10 ? 8 : 16);
    for (i = 0; i < bytes.length; i++) push(bytes[i], 8);
    var maxBits = dataCount * 8;
    if (bits.length + 4 <= maxBits) push(0, 4);
    while (bits.length % 8) bits.push(0);
    var pad = [0xec, 0x11];
    var p = 0;
    while (bits.length < maxBits) push(pad[p++ % 2], 8);
    var data = bitsToBytes(bits).slice(0, dataCount);
    var blockData = [];
    var blockEcc = [];
    var base = Math.floor(dataCount / blocks);
    var extra = dataCount % blocks;
    var offset = 0;
    for (i = 0; i < blocks; i++) {
      var sz = base + (i >= blocks - extra ? 1 : 0);
      var chunk = data.slice(offset, offset + sz);
      offset += sz;
      blockData.push(chunk);
      blockEcc.push(rs(chunk, eccLen));
    }
    var inter = [];
    var maxD = Math.max.apply(null, blockData.map(function (b) { return b.length; }));
    for (i = 0; i < maxD; i++) {
      for (var b = 0; b < blocks; b++) if (i < blockData[b].length) inter.push(blockData[b][i]);
    }
    for (i = 0; i < eccLen; i++) {
      for (b = 0; b < blocks; b++) inter.push(blockEcc[b][i]);
    }
    return inter;
  }

  function finder(mod, size, x, y) {
    for (var r = -1; r < 8; r++) {
      for (var c = -1; c < 8; c++) {
        var rr = y + r, cc = x + c;
        if (rr < 0 || cc < 0 || rr >= size || cc >= size) continue;
        var on = (r >= 0 && r <= 6 && c >= 0 && c <= 6) &&
          (r === 0 || r === 6 || c === 0 || c === 6 || (r >= 2 && r <= 4 && c >= 2 && c <= 4));
        mod[rr][cc] = on ? 1 : 0;
      }
    }
  }

  function reserve(mod, size, ver) {
    var rsv = [];
    function mark(r, c) { rsv[r + "," + c] = true; }
    for (var i = 0; i < 8; i++) {
      mark(8, i); mark(i, 8); mark(8, size - 1 - i); mark(size - 1 - i, 8);
    }
    mark(8, 8);
    for (i = 0; i < size; i++) { mark(6, i); mark(i, 6); }
    if (ver >= 7) {
      for (var a = 0; a < 6; a++) for (var b = 0; b < 3; b++) {
        mark(a, size - 11 + b); mark(size - 11 + b, a);
      }
    }
    return rsv;
  }

  function build(text) {
    var bytes = text.length;
    var ver = 1;
    for (; ver <= 10; ver++) {
      var cap = ECC[ver][0] - (ver < 10 ? 2 : 3);
      if (bytes <= cap) break;
    }
    if (ver > 10) ver = 10;
    var size = ver * 4 + 17;
    var mod = [];
    var locked = [];
    var r, c;
    for (r = 0; r < size; r++) {
      mod[r] = [];
      locked[r] = [];
      for (c = 0; c < size; c++) { mod[r][c] = 0; locked[r][c] = false; }
    }
    function set(rr, cc, v) { mod[rr][cc] = v ? 1 : 0; locked[rr][cc] = true; }
    finder(mod, size, 0, 0); finder(mod, size, size - 7, 0); finder(mod, size, 0, size - 7);
    for (r = 0; r < 9; r++) for (c = 0; c < 9; c++) {
      if (r < size && c < size) locked[r][c] = true;
      if (c < 8) locked[r][size - 8 + c] = true;
      if (r < 8) locked[size - 8 + r][c] = true;
    }
    for (i = 0; i < size; i++) { set(6, i, i % 2 === 0); set(i, 6, i % 2 === 0); }
    var pos = ALIGN[ver] || [];
    for (var i = 0; i < pos.length; i++) {
      for (var j = 0; j < pos.length; j++) {
        var y = pos[i], x = pos[j];
        if ((y < 8 && x < 8) || (y < 8 && x > size - 9) || (y > size - 9 && x < 8)) continue;
        for (r = -2; r <= 2; r++) for (c = -2; c <= 2; c++) {
          set(y + r, x + c, Math.max(Math.abs(r), Math.abs(c)) !== 1);
        }
      }
    }
    var rsv = reserve(mod, size, ver);
    var data = encode(text, ver);
    var bit = 0;
    var dir = -1;
    var col = size - 1;
    function need(rr, cc) { return !locked[rr][cc] && !rsv[rr + "," + cc]; }
    while (col > 0) {
      if (col === 6) col--;
      for (var n = 0; n < size; n++) {
        r = dir < 0 ? size - 1 - n : n;
        for (var k = 0; k < 2; k++) {
          c = col - k;
          if (!need(r, c)) continue;
          var b = (data[bit >> 3] >> (7 - (bit & 7))) & 1;
          mod[r][c] = b;
          bit++;
        }
      }
      col -= 2;
      dir = -dir;
    }
    var mask = 0;
    for (r = 0; r < size; r++) {
      for (c = 0; c < size; c++) {
        if (locked[r][c] || rsv[r + "," + c]) continue;
        if (((r + c) % 2) === 0) mod[r][c] ^= 1;
      }
    }
    var fmt = 0x5412 ^ 0x77c4;
    /* format bits for mask 0, EC level M (01) approximated via BCH 0x5412 pattern; draw known good format for mask 0 / M */
    fmt = 0x5412;
    var bitsFmt = [];
    for (i = 14; i >= 0; i--) bitsFmt.push((fmt >> i) & 1);
    var mapA = [[0,8],[1,8],[2,8],[3,8],[4,8],[5,8],[7,8],[8,8],[8,7],[8,5],[8,4],[8,3],[8,2],[8,1],[8,0]];
    var mapB = [[8,size-1],[8,size-2],[8,size-3],[8,size-4],[8,size-5],[8,size-6],[8,size-7],[size-8,8],[size-7,8],[size-6,8],[size-5,8],[size-4,8],[size-3,8],[size-2,8],[size-1,8]];
    for (i = 0; i < 15; i++) {
      mod[mapA[i][1]][mapA[i][0]] = bitsFmt[i];
      mod[mapB[i][1]][mapB[i][0]] = bitsFmt[i];
    }
    mod[size - 8][8] = 1;
    return { size: size, mod: mod };
  }

  MC.drawQR = function (canvas, text) {
    if (!canvas || !text) return;
    var qr = build(String(text));
    var size = qr.size;
    var pad = 2;
    var dim = canvas.width || 220;
    canvas.height = dim;
    var ctx = canvas.getContext("2d");
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, dim, dim);
    var cell = dim / (size + pad * 2);
    ctx.fillStyle = "#0B2E2B";
    for (var r = 0; r < size; r++) {
      for (var c = 0; c < size; c++) {
        if (qr.mod[r][c]) {
          ctx.fillRect((c + pad) * cell, (r + pad) * cell, cell + 0.4, cell + 0.4);
        }
      }
    }
  };
})(window);
