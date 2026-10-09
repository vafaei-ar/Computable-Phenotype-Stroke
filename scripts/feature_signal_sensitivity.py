#!/usr/bin/env python3
"""Exploratory feature-signal and selection sensitivity for long-format monthly aggregates.

Nested phenotype ratios describe recorded feature signals. They do not independently
measure EHR data completeness or actual clinical service utilization.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

ALL_DEFS = [f"D{i}" for i in range(9)]
NON_MRI_REQUIRED = ["D0", "D1", "D2", "D5", "D8"]
FEATURE_RATIOS = [("D7", "D5", "MRI signal / broad imaging"),
                  ("D3", "D1", "MRI-plus-lipid / broad imaging-plus-lipid"),
                  ("D6", "D3", "rehabilitation / MRI-plus-lipid")]

def load_counts(path: str | Path) -> pd.DataFrame:
    raw = pd.read_csv(path, dtype={"center_id": str, "month": str, "definition_id": str})
    required = {"center_id", "month", "definition_id", "phenotype_count", "registry_count"}
    if missing := required - set(raw.columns):
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if raw[list(required)].isna().any().any():
        raise ValueError("Required fields contain missing values")
    if raw.duplicated(["center_id", "month", "definition_id"]).any():
        raise ValueError("Duplicate center/month/definition combinations")
    for col in ("phenotype_count", "registry_count"):
        raw[col] = pd.to_numeric(raw[col], errors="raise")
        if (raw[col] < 0).any(): raise ValueError("Negative counts")
    if not raw["month"].str.fullmatch(r"\d{4}-\d{2}").all():
        raise ValueError("Months must use YYYY-MM")
    check = raw.groupby(["center_id", "month"])["registry_count"].nunique()
    if (check != 1).any():
        raise ValueError("Registry count differs between definitions for the same center-month")
    return raw.sort_values(["center_id", "month", "definition_id"]).reset_index(drop=True)

def metrics(raw: pd.DataFrame, center_id: str, min_month: str | None = None) -> pd.DataFrame:
    data = raw.loc[raw.center_id == str(center_id)]
    if min_month: data = data.loc[data.month >= min_month]
    if data.empty: raise ValueError(f"No monthly counts for {center_id} >= {min_month}")
    rows=[]
    for definition,g in data.groupby("definition_id"):
        ref=g.registry_count.to_numpy(float)
        pred=g.phenotype_count.to_numpy(float)
        if not ref.sum(): continue
        err=np.abs(pred-ref)
        rows.append({"definition_id": definition, "months":len(g),
                     "MAE":float(err.mean()), "nMAE_percent":float(100*err.sum()/ref.sum()),
                     "count_ratio":float(pred.sum()/ref.sum())})
    m = pd.DataFrame(rows).sort_values(["nMAE_percent", "definition_id"]).reset_index(drop=True)
    m["nMAE_rank"] = m["nMAE_percent"].rank(method="min").astype(int)
    return m

def ratios(raw: pd.DataFrame) -> pd.DataFrame:
    counts = raw.groupby(["center_id", "definition_id"])["phenotype_count"].sum().unstack()
    rows=[]
    for center,counts_at in counts.iterrows():
        for numerator, denominator, label in FEATURE_RATIOS:
            if numerator not in counts_at.index or denominator not in counts_at.index:
                val=np.nan
            else:
                n=counts_at[numerator]; d=counts_at[denominator]
                val=100*n/d if pd.notna(n) and pd.notna(d) and d>0 else np.nan
            rows.append({"center_id":center,"signal":label,"subset":numerator,
                         "parent":denominator,"ratio_percent":val})
    return pd.DataFrame(rows)

def policies(raw: pd.DataFrame, allowed: list[str], label: str):
    m=pd.concat([metrics(raw,c).assign(center_id=c) for c in sorted(raw.center_id.unique())])
    n=m.pivot(index="definition_id",columns="center_id",values="nMAE_percent")
    n=n.loc[allowed].dropna()
    if len(n)!=len(allowed): raise ValueError("At least one candidate not available at all centers")
    select=lambda s: sorted(s.items(),key=lambda v:(v[1],v[0]))[0][0]
    mean=n.mean(axis=1); worst=n.max(axis=1)
    u=select(mean.to_dict());r=select(worst.to_dict())
    rec=[]
    for center in n.columns:
        other=n.drop(columns=center).mean(axis=1)
        chosen=select(other.to_dict());local=select(n[center].to_dict())
        rec.append({"candidate_set":label,"held_out_center":center,
                    "selected_from_other_centers":chosen,
                    "held_out_nMAE_percent":float(n.loc[chosen,center]),
                    "local_best":local,"local_nMAE_percent":float(n.loc[local,center]),
                    "regret_pp":float(n.loc[chosen,center]-n.loc[local,center])})
    policy={"candidate_set":label,"candidate_definitions":", ".join(allowed),
            "universal":u,"universal_mean_nMAE_percent":float(mean[u]),
            "minimax":r,"minimax_worst_nMAE_percent":float(worst[r]),
            "mean_LOCO_regret_pp":float(np.mean([row["regret_pp"] for row in rec])),
            "max_LOCO_regret_pp":float(max(row["regret_pp"] for row in rec))}
    return policy,pd.DataFrame(rec)

def run(raw: pd.DataFrame, output_dir: Path, center1: str = "1"):
    output_dir.mkdir(parents=True,exist_ok=True)
    ratios(raw).to_csv(output_dir/"nested_feature_signal_ratios.csv",index=False)
    reports=[]
    for label,month in [("primary",None),("start_may_2018","2018-05"),("start_june_2018","2018-06")]:
        m=metrics(raw,center1,min_month=month)
        for row in m.to_dict("records"):
            reports.append(dict(center_id=center1,window=label,**row))
    pd.DataFrame(reports).to_csv(output_dir/"center1_common_window_rankings.csv",index=False)
    allcent=sorted(raw.center_id.unique())
    present={c:set(raw.loc[raw.center_id==c,"definition_id"]) for c in allcent}
    common=sorted(set.intersection(*present.values()))
    p0,l0=policies(raw,common,"primary_common")
    p1,l1=policies(raw,NON_MRI_REQUIRED,"no_mandatory_MRI")
    pd.DataFrame([p0,p1]).to_csv(output_dir/"candidate_set_policy_sensitivity.csv",index=False)
    pd.concat([l0,l1]).to_csv(output_dir/"candidate_set_LOCO_sensitivity.csv",index=False)
    print("Feature-signal sensitivity outputs written to",output_dir)
    return p0,p1

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True,help="Long-format center-month-definition count CSV or CSV.gz")
    ap.add_argument("--output-dir",required=True)
    ap.add_argument("--center1",default="1",help="Center identifier for window analysis; default 1")
    args=ap.parse_args()
    run(load_counts(args.input),Path(args.output_dir),args.center1)

if __name__=="__main__":main()
