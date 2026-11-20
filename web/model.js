/* Pure calculation layer: mirrors the DAX measures in /dax. */
(function (g) {
function Model(D) {
  const T = D.territories, wk = D.weeks, W = wk.length, L = wk[W - 1], Q = D.quarterStart, all = T.map((_, i) => i);
  const rng = (a, b) => wk.map((d, i) => (d >= a && d <= b ? i : -1)).filter(i => i >= 0);
  const yr = +L.slice(0, 4), M = { cur: rng(wk[W - 13], L), pri: rng(wk[W - 26], wk[W - 14]),
    ytd: rng(yr + "-01-01", L), ly: rng(yr - 1 + "-01-01", yr - 1 + L.slice(4)), qtd: rng(Q, L) };
  const sum = (ts, ps, ix) => { let s = 0; for (const p of ps) for (const t of ts) for (const w of ix) s += D.trx[p][t][w]; return s; };
  const day = s => Date.UTC(+s.slice(0, 4), +s.slice(5, 7) - 1, +s.slice(8, 10)) / 864e5;
  const qEnd = Date.UTC(+Q.slice(0, 4), +Q.slice(5, 7) + 2, 0) / 864e5;
  const elapsed = (day(L) - day(Q) + 1) / (qEnd - day(Q) + 1);
  const dense = (arr, f, asc) => { const v = [...new Set(arr.map(f))].sort((a, b) => (asc ? a - b : b - a)); return x => v.indexOf(f(x)) + 1; };

  function compute(s) {
    const ps = s.prod ? [s.prod - 1] : [0, 1];
    const sel = all.filter(i => (!s.region || T[i].region === s.region) && (!s.terr || T[i].id === +s.terr));
    const regs = new Set(sel.map(i => T[i].region)), R = all.filter(i => regs.has(T[i].region));
    const lv = [["Territory", sel, 1], ["Region (Avg)", R, R.length], ["Nation (Avg)", all, all.length]];
    const cmp = lv.map(([n, ts, k]) => { const f = m => sum(ts, ps, M[m]) / k, c = f("cur"), p = f("pri"), y = f("ytd"), l = f("ly");
      return { n, c, chg: p ? (c - p) / p : null, y, yoy: l ? (y - l) / l : null }; });
    const goal = ts => ps.reduce((a, p) => a + ts.reduce((b, t) => b + D.goals[p][t], 0), 0);
    const gl = ts => { const q = sum(ts, ps, M.qtd), g = goal(ts); return { q, g, pct: g ? q / g : null }; };
    const goals = { terr: gl(sel), region: gl(R), nation: gl(all), elapsed };
    const ix = rng(s.from, s.to), months = [...new Set(ix.map(i => wk[i].slice(0, 7)))];
    const ser = (ts, k) => months.map(m => sum(ts, ps, ix.filter(i => wk[i].startsWith(m))) / k);
    const trend = { months, terr: ser(sel, 1), region: ser(R, R.length), nation: ser(all, all.length) };
    const H = D.hcps, selSet = new Set(sel.map(i => i + 1)), win = s.win === "QTD" ? [16, 17] : [14, 15];
    const reach = pred => ["A", "B", "C"].map(tr => { let n = 0, r = 0, c = 0;
      for (const h of H) { if (h[4] !== tr || !pred(h)) continue; n++; const k = ps.reduce((a, p) => a + h[win[p]], 0); if (k > 0) { r++; c += k; } }
      return { reach: n ? r / n : null, freq: r ? c / r : null }; });
    const regSet = new Set(R.map(i => i + 1));
    const rc = { terr: reach(h => selSet.has(h[5])), region: reach(h => regSet.has(h[5])), nation: reach(() => true) };
    const rows = H.filter(h => selSet.has(h[5])).map(h => { const x = o => ps.reduce((a, p) => a + h[o + p], 0), cur = x(6), pr = x(8);
      return { name: h[1], city: h[2], spec: h[3], tier: h[4], cur, chg: cur - pr, pr, bef: x(10),
        lc: ps.map(p => h[12 + p]).filter(Boolean).sort().pop() || "", c8: x(14) }; });
    let out;
    if (s.view === "New Writers") out = rows.filter(r => r.cur > 0 && r.bef === 0).sort((a, b) => b.cur - a.cur);
    else if (s.view === "Top Writers") { const p = rows.filter(r => r.cur > 0), rk = dense(p, r => r.cur, false); out = p.filter(r => rk(r) <= 10).sort((a, b) => b.cur - a.cur); }
    else { const dec = s.view === "Decliners", p = rows.filter(r => r.cur > 0 || r.pr > 0), rk = dense(p, r => r.chg, dec);
      out = p.filter(r => rk(r) <= 10 && (dec ? r.chg < 0 : r.chg > 0)).sort((a, b) => (dec ? a.chg - b.chg : b.chg - a.chg)); }
    return { cmp, goals, trend, rc, writers: out };
  }
  return { compute, T };
}
if (typeof module !== "undefined") module.exports = Model; else g.Model = Model;
})(this);
