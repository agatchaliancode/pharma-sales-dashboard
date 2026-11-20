"""Aggregates the CSVs in /data into web/data.json (small, browser-friendly)."""
import json, pandas as pd, numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; D = ROOT/"data"
f = pd.read_csv(D/"fact_trx_weekly.csv", parse_dates=["week_ending_date"])
h = pd.read_csv(D/"dim_hcp.csv"); t = pd.read_csv(D/"dim_territory.csv"); p = pd.read_csv(D/"dim_product.csv")
c = pd.read_csv(D/"fact_calls.csv", parse_dates=["call_date"]); q = pd.read_csv(D/"fact_quota.csv")
weeks = sorted(f.week_ending_date.unique()); W = len(weeks); wi = {w: i for i, w in enumerate(weeks)}
L = pd.Timestamp(weeks[-1]); QS = L.to_period("Q").start_time
f = f.merge(h[["hcp_id", "territory_id"]]); f["w"] = f.week_ending_date.map(wi)
trx = np.zeros((2, len(t), W), dtype=int)
for (pr, tr, w), v in f.groupby(["product_id", "territory_id", "w"]).trx.sum().items(): trx[pr-1, tr-1, w] = v
def win(lo, hi): return f[(f.w >= lo) & (f.w <= hi)].groupby(["hcp_id", "product_id"]).trx.sum()
cur, pri, bef = win(W-13, W-1), win(W-26, W-14), win(0, W-14)
c8 = c[(c.call_date >= L - pd.Timedelta(days=55)) & (c.call_date <= L)].groupby(["hcp_id", "product_id"]).size()
cq = c[(c.call_date >= QS) & (c.call_date <= L)].groupby(["hcp_id", "product_id"]).size()
last = c.groupby(["hcp_id", "product_id"]).call_date.max()
g = lambda s, i, pr: int(s.get((i, pr), 0))
rows = [[int(r.hcp_id), r.hcp_name, r.city, r.specialty, r.priority_tier, int(r.territory_id)]
        + [g(cur, r.hcp_id, k) for k in (1, 2)] + [g(pri, r.hcp_id, k) for k in (1, 2)] + [g(bef, r.hcp_id, k) for k in (1, 2)]
        + [(last[(r.hcp_id, k)].strftime("%Y-%m-%d") if (r.hcp_id, k) in last.index else None) for k in (1, 2)]
        + [g(c8, r.hcp_id, k) for k in (1, 2)] + [g(cq, r.hcp_id, k) for k in (1, 2)] for r in h.itertuples()]
gq = q[q.quarter_start_date == QS.strftime("%Y-%m-%d")]
goals = [[int(gq[(gq.product_id == k) & (gq.territory_id == tid)].trx_goal.sum()) for tid in t.territory_id] for k in (1, 2)]
out = {"weeks": [pd.Timestamp(w).strftime("%Y-%m-%d") for w in weeks], "quarterStart": QS.strftime("%Y-%m-%d"),
       "territories": [{"id": int(r.territory_id), "name": r.territory_name, "region": r.region_name} for r in t.itertuples()],
       "products": [r.product_name for r in p.itertuples()], "trx": trx.tolist(), "goals": goals,
       "hcpFields": "id,name,city,specialty,tier,terr,cur1,cur2,pri1,pri2,bef1,bef2,last1,last2,c8_1,c8_2,cq1,cq2",
       "hcps": rows, "asOf": {"final": "2026-10-31", "prelim": L.strftime("%Y-%m-%d"), "calls": c.call_date.max().strftime("%Y-%m-%d")}}
(ROOT/"web"/"data.json").write_text(json.dumps(out, separators=(",", ":")))
