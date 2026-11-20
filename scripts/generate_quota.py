"""Quarterly TRx goals: prior-quarter actuals x a random uplift (seeded)."""
import pandas as pd, numpy as np
from pathlib import Path
D = Path(__file__).resolve().parent.parent / "data"
rng = np.random.default_rng(77)
f = pd.read_csv(D/"fact_trx_weekly.csv", parse_dates=["week_ending_date"])
h = pd.read_csv(D/"dim_hcp.csv"); t = pd.read_csv(D/"dim_territory.csv")
f = f.merge(h[["hcp_id","territory_id"]])
f["q"] = f.week_ending_date.dt.to_period("Q").dt.start_time
act = f.groupby(["territory_id","product_id","q"]).trx.sum()
qs = pd.date_range("2024-01-01","2026-10-01",freq="QS"); rows = []
for tid in t.territory_id:
    for p in (1,2):
        for i,q in enumerate(qs):
            base = act.get((tid,p,qs[i-1]),0) if i>0 else act.get((tid,p,q),0)
            if i>0 and base==0: base = act.get((tid,p,q),0)
            g = int(round(base*rng.uniform(0.97,1.10))) if i>0 else int(round(base*rng.uniform(0.95,1.05)))
            rows.append(dict(territory_id=tid,product_id=p,quarter_start_date=q.date().isoformat(),
                             quarter_label=f"{q.year} Q{(q.month-1)//3+1}",trx_goal=g))
fq = pd.DataFrame(rows); fq.insert(0,"quota_id",range(1,len(fq)+1))
fq.to_csv(D/"fact_quota.csv", index=False)
