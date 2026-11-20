import numpy as np, pandas as pd
from datetime import date, timedelta
rng = np.random.default_rng(2026)
from pathlib import Path
OUT = str(Path(__file__).resolve().parent.parent / "data") + "/"
START, END = date(2024,1,1), date(2026,11,15)

# ---------- dim_date ----------
days = pd.date_range(START, END, freq="D")
d = pd.DataFrame({"date_key": days})
d["week_start_date"] = d.date_key - pd.to_timedelta(d.date_key.dt.weekday, unit="D")
d["week_ending_date"] = d.week_start_date + pd.Timedelta(days=6)
d["year"] = d.date_key.dt.year
d["quarter"] = d.date_key.dt.quarter
d["quarter_label"] = d.year.astype(str) + " Q" + d.quarter.astype(str)
d["quarter_start_date"] = d.date_key.dt.to_period("Q").dt.start_time
d["month_num"] = d.date_key.dt.month
d["month_name"] = d.date_key.dt.strftime("%b")
d["month_start_date"] = d.date_key.dt.to_period("M").dt.start_time
d["year_month"] = d.date_key.dt.strftime("%Y-%m")
d["day_name"] = d.date_key.dt.strftime("%a")
d["is_weekend"] = d.date_key.dt.weekday >= 5
d.to_csv(OUT+"dim_date.csv", index=False, date_format="%Y-%m-%d")

weeks = sorted(d.week_ending_date.unique())
weeks = [pd.Timestamp(w) for w in weeks]
W = len(weeks); print("weeks", W, weeks[0].date(), weeks[-1].date())

# ---------- territories ----------
terr_def = {
 "Northeast": {"Boston MA":["Boston","Cambridge","Newton","Framingham","Concord","Shrewsbury","North Chelmsford","Quincy"],
               "New York NY":["New York","Brooklyn","Bronx","Queens","Yonkers","White Plains"],
               "Long Island NY":["Hempstead","Huntington","Islip","Babylon","Garden City"],
               "Philadelphia PA":["Philadelphia","Norristown","Media","Doylestown","King of Prussia"],
               "Pittsburgh PA":["Pittsburgh","Cranberry Township","Monroeville","Bethel Park"],
               "Newark NJ":["Newark","Paramus","Edison","Hackensack","Morristown"]},
 "Southeast": {"Atlanta GA":["Atlanta","Marietta","Decatur","Alpharetta","Roswell"],
               "Miami FL":["Miami","Coral Gables","Hialeah","Fort Lauderdale","Hollywood"],
               "Tampa FL":["Tampa","Clearwater","St. Petersburg","Brandon","Lakeland"],
               "Charlotte NC":["Charlotte","Concord","Gastonia","Huntersville","Matthews"],
               "Nashville TN":["Nashville","Franklin","Murfreesboro","Brentwood","Hendersonville"],
               "Orlando FL":["Orlando","Kissimmee","Winter Park","Sanford","Lake Mary"]},
 "Midwest":   {"Chicago IL":["Chicago","Evanston","Oak Park","Naperville","Schaumburg"],
               "Detroit MI":["Detroit","Troy","Ann Arbor","Dearborn","Southfield"],
               "Minneapolis MN":["Minneapolis","St. Paul","Bloomington","Edina","Plymouth"],
               "Columbus OH":["Columbus","Dublin","Westerville","Hilliard","Grove City"],
               "St. Louis MO":["St. Louis","Clayton","Chesterfield","St. Charles","Florissant"],
               "Indianapolis IN":["Indianapolis","Carmel","Fishers","Greenwood","Noblesville"]},
 "Southwest": {"Dallas TX":["Dallas","Plano","Irving","Frisco","Garland"],
               "Houston TX":["Houston","Sugar Land","The Woodlands","Katy","Pearland"],
               "Austin TX":["Austin","Round Rock","Cedar Park","Georgetown","San Marcos"],
               "Phoenix AZ":["Phoenix","Scottsdale","Mesa","Chandler","Tempe"],
               "Denver CO":["Denver","Aurora","Lakewood","Boulder","Littleton"],
               "Oklahoma City OK":["Oklahoma City","Edmond","Norman","Moore","Midwest City"]},
 "West":      {"Los Angeles CA":["Los Angeles","Pasadena","Glendale","Santa Monica","Torrance"],
               "San Diego CA":["San Diego","La Jolla","Carlsbad","Chula Vista","Escondido"],
               "San Francisco CA":["San Francisco","Oakland","San Mateo","Berkeley","Walnut Creek"],
               "Seattle WA":["Seattle","Bellevue","Tacoma","Everett","Kirkland"],
               "Portland OR":["Portland","Beaverton","Hillsboro","Lake Oswego","Gresham"],
               "Las Vegas NV":["Las Vegas","Henderson","North Las Vegas","Summerlin","Boulder City"]}}
terr_rows, region_ids = [], {r:i+1 for i,r in enumerate(terr_def)}
tid = 0
for reg, ts in terr_def.items():
    for tn, cities in ts.items():
        tid += 1
        terr_rows.append(dict(territory_id=tid, territory_code=f"{reg[:2].upper()}{tid:02d}", territory_name=tn,
                              region_id=region_ids[reg], region_name=reg, cities=cities))
dt = pd.DataFrame(terr_rows)
dt.drop(columns="cities").to_csv(OUT+"dim_territory.csv", index=False)
T = len(dt)

# ---------- products ----------
dp = pd.DataFrame([
 dict(product_id=1, product_name="Neurovia", therapeutic_area="Neuroscience", launch_date="2022-03-01"),
 dict(product_id=2, product_name="Cardiolex", therapeutic_area="Cardiometabolic", launch_date="2023-09-01")])
dp.to_csv(OUT+"dim_product.csv", index=False)

# ---------- reps ----------
first = ["James","Maria","Robert","Linda","Michael","Patricia","David","Jennifer","Daniel","Priya","Kevin","Aisha","Brian","Sofia","Marcus","Emily","Tyler","Grace","Omar","Hannah","Carlos","Rachel","Jason","Nina","Eric","Tanya","Victor","Alyssa","Derek","Monica"]
last = ["Anderson","Brooks","Chen","Diaz","Edwards","Foster","Garcia","Hughes","Ito","Johnson","Kim","Lopez","Mitchell","Nguyen","Owens","Patel","Quinn","Reyes","Singh","Turner","Usman","Vargas","Walker","Xu","Young","Zimmerman","Bennett","Cohen","Dunn","Ellis"]
reps = []
for i,row in dt.iterrows():
    reps.append(dict(rep_id=row.territory_id, rep_name=f"{first[(i*7)%30]} {last[(i*11+3)%30]}", territory_id=row.territory_id,
                     hire_date=(date(2019,1,1)+timedelta(days=int(rng.integers(0,1800)))).isoformat(), job_title="Territory Business Manager"))
pd.DataFrame(reps).to_csv(OUT+"dim_rep.csv", index=False)

# ---------- HCPs ----------
specs = ["Psychiatry","Neurology","Pediatrics","Internal Medicine","Family Medicine","Rheumatology","Cardiology","Endocrinology","Sports Medicine (Internal Medicine)"]
sp_w  = [.18,.12,.08,.20,.20,.05,.09,.06,.02]
aff = {  # affinity (product1, product2)
 "Psychiatry":(1.0,.10),"Neurology":(.9,.15),"Pediatrics":(.5,.05),"Internal Medicine":(.35,.8),"Family Medicine":(.5,.6),
 "Rheumatology":(.2,.3),"Cardiology":(.05,1.0),"Endocrinology":(.1,.9),"Sports Medicine (Internal Medicine)":(.3,.3)}
tier_names = ["A","B","C","NP"]; tier_p = [.08,.17,.25,.50]
base = {"A":2.2,"B":1.2,"C":0.6,"NP":0.12}
hcps = []
hid = 0
used=set()
for _,tr in dt.iterrows():
    n = int(rng.integers(52,78))
    for _ in range(n):
        hid += 1
        while True:
            nm = f"{first[rng.integers(30)]} {last[rng.integers(30)]}"
            cred = rng.choice(["MD","DO","NP","PA"], p=[.72,.1,.12,.06])
            full = f"{nm}, {cred}"
            if full not in used: used.add(full); break
        hcps.append(dict(hcp_id=hid, npi_number=str(1000000000+int(rng.integers(0,899999999))), hcp_name=full,
                         credential=cred, specialty=rng.choice(specs,p=sp_w), city=rng.choice(tr.cities),
                         priority_tier=rng.choice(tier_names,p=tier_p), territory_id=tr.territory_id))
dh = pd.DataFrame(hcps)
# NP/PA prescribers -> primary-care style specialty mix is fine; tier driven by tier
dh.to_csv(OUT+"dim_hcp.csv", index=False)
H = len(dh); print("HCPs", H)

# ---------- TRx ----------
t = np.arange(W)/(W-1)
woy = np.array([w.isocalendar()[1] for w in weeks])
season = 1+0.07*np.sin(2*np.pi*(woy-10)/52) 
season[(woy>=52)|(woy<=1)] *= 0.85
g = np.vstack([1+0.18*t, 0.45+1.0*t**0.8])        # product growth curves (P,W)
terr_f = np.exp(rng.normal(0,.22,T)); terr_slope = rng.uniform(-.30,.35,T)
terr_idx = dh.territory_id.values-1
hb = dh.priority_tier.map(base).values
hcp_slope = rng.normal(0,.35,H)
start = np.zeros(H,dtype=int); stop = np.full(H,10**6)
tier = dh.priority_tier.values
for i in range(H):
    r = rng.random()
    if tier[i]=="NP":
        if r<.14: start[i]=10**6               # never writes
        elif r<.24: start[i]=int(rng.integers(W-13,W))   # NEW writers in last 13 wks
        elif r<.50: start[i]=int(rng.integers(0,W-13))
    elif tier[i]=="C":
        if r<.08: start[i]=int(rng.integers(W-13,W))
        elif r<.30: start[i]=int(rng.integers(0,W-13))
    elif tier[i]=="B" and r<.12: start[i]=int(rng.integers(0,W-13))
    if start[i]<W-25 and rng.random()<.07: stop[i]=int(rng.integers(max(start[i]+10,W//2),W))
A = np.array([aff[s] for s in dh.specialty]).T       # (P,H)
rows=[]
for p in range(2):
    lam = (hb*A[p])[:,None] * terr_f[terr_idx][:,None] \
        * np.exp(terr_slope[terr_idx][:,None]*(t[None,:]-.5)) \
        * np.exp(hcp_slope[:,None]*(t[None,:]-.5)) * g[p][None,:] * season[None,:]
    wk = np.arange(W)[None,:]
    lam = lam * ((wk>=start[:,None]) & (wk<stop[:,None]))
    # decaying before stop (decliner behaviour)
    lam = lam * np.where((stop[:,None]<10**6)&(wk>=stop[:,None]-12)&(wk<stop[:,None]), 0.5, 1)
    y = rng.poisson(lam)
    rows.append(y)
Y = np.stack(rows)            # (P,H,W)
# guarantee first week of a late starter has >=1 TRx
for i in range(H):
    if start[i]<W:
        if Y[:,i,start[i]].sum()==0: Y[int(np.argmax(A[:,i])), i, start[i]] = 1
pi,hi,wi = np.nonzero(Y)
final_cut = pd.Timestamp("2026-11-01")
ft = pd.DataFrame({"week_ending_date":[weeks[k] for k in wi],"hcp_id":dh.hcp_id.values[hi],"product_id":pi+1,"trx":Y[pi,hi,wi]})
ft["data_status"] = np.where(ft.week_ending_date<=final_cut,"Final","Preliminary")
ft = ft.sort_values(["week_ending_date","hcp_id","product_id"])
ft.to_csv(OUT+"fact_trx_weekly.csv", index=False, date_format="%Y-%m-%d")
print("trx rows", len(ft))

# ---------- Calls ----------
cl = {"A":1.05,"B":.65,"C":.40,"NP":.06}
eff = rng.uniform(.85,1.1,T)
vac = np.ones((T,W))
vac_terrs = rng.choice(T,6,replace=False)
for k,tix in enumerate(vac_terrs):
    ln = int(rng.integers(8,14)); s = int(rng.integers(W-20,W-ln)) if k<2 else int(rng.integers(10,W-ln-20))
    vac[tix,s:s+ln]=0.05
holiday = np.where((woy>=52)|(woy<=1),0.5,1.0)
lamc = np.array([cl[x] for x in tier])[:,None]*eff[terr_idx][:,None]*vac[terr_idx,:]*holiday[None,:]
C = rng.poisson(lamc)
hi,wi = np.nonzero(C); cnt = C[hi,wi]
hi = np.repeat(hi,cnt); wi = np.repeat(wi,cnt)
n = len(hi)
dow = rng.integers(0,5,n)
call_dates = [weeks[k]-pd.Timedelta(days=6)+pd.Timedelta(days=int(o)) for k,o in zip(wi,dow)]
pw = A[:,hi].T; pw = pw/pw.sum(1,keepdims=True)
prod = 1+(rng.random(n)>pw[:,0]).astype(int)
fc = pd.DataFrame({"call_date":call_dates,"hcp_id":dh.hcp_id.values[hi],
                   "rep_id":dh.territory_id.values[hi],"product_id":prod,
                   "call_type":rng.choice(["In-Person","Virtual","Lunch & Learn"],n,p=[.68,.27,.05])})
fc = fc.sort_values(["call_date","hcp_id"]).reset_index(drop=True)
fc.insert(0,"call_id",np.arange(1,len(fc)+1))
fc.to_csv(OUT+"fact_calls.csv", index=False, date_format="%Y-%m-%d")
print("call rows", len(fc), fc.call_date.min().date(), fc.call_date.max().date())

pd.DataFrame([dict(dataset_name="Monthly Data",latest_data_date="2026-10-31"),
              dict(dataset_name="Prelim Data",latest_data_date="2026-11-15"),
              dict(dataset_name="Call Data",latest_data_date="2026-11-15")]).to_csv(OUT+"data_refresh.csv",index=False)

# ---------- sanity ----------
L = weeks[-1]
cur = ft[ft.week_ending_date>L-pd.Timedelta(days=91)]
pri = ft[(ft.week_ending_date<=L-pd.Timedelta(days=91))&(ft.week_ending_date>L-pd.Timedelta(days=182))]
c = cur.groupby("hcp_id").trx.sum(); pr = pri.groupby("hcp_id").trx.sum()
life_before = ft[ft.week_ending_date<=L-pd.Timedelta(days=91)].groupby("hcp_id").trx.sum()
new = [h for h in c.index if h not in life_before.index]
print("new writers nationally:", len(new))
x = pd.DataFrame({"c":c,"p":pr}).fillna(0); x["d"]=x.c-x.p
print("gainers",(x.d>0).sum(),"decliners",(x.d<0).sum())
terr_c = cur.merge(dh[["hcp_id","territory_id"]]).groupby("territory_id").trx.sum()
print("terr 13wk TRx min/med/max", terr_c.min(), terr_c.median(), terr_c.max())
w8 = fc[fc.call_date>=pd.Timestamp(L)-pd.Timedelta(days=55)].merge(dh[["hcp_id","priority_tier"]])
for tr_ in "ABC":
    nh = (dh.priority_tier==tr_).sum(); s = w8[w8.priority_tier==tr_]
    print(tr_, "reach", round(s.hcp_id.nunique()/nh,3), "freq", round(len(s)/s.hcp_id.nunique(),2))
print("Boston terr id", dt[dt.territory_name=="Boston MA"].territory_id.iloc[0])
