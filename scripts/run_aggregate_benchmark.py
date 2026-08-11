#!/usr/bin/env python3
"""Aggregate benchmarking utilities for multisite computable phenotype evaluation."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import kendalltau, spearmanr

LOGICAL_CHECKS = [("D1","D5"),("D3","D7"),("D3","D1"),("D4","D7"),("D6","D3"),("D6","D4"),("D8","D1"),("D2","D5"),("D1","D2"),("D3","D4")]

def lin_ccc(x, y):
    x=np.asarray(x,dtype=float); y=np.asarray(y,dtype=float)
    if len(x)<2 or np.var(x)==0 or np.var(y)==0: return np.nan
    mx,my=x.mean(),y.mean(); vx,vy=x.var(ddof=1),y.var(ddof=1); cov=np.cov(x,y,ddof=1)[0,1]
    return float((2*cov)/(vx+vy+(mx-my)**2))

def calc_metrics(df):
    rows=[]
    for (center,definition),g in df.groupby(["center_id","definition_id"]):
        pred=g["phenotype_count"].to_numpy(float); ref=g["registry_count"].to_numpy(float); err=pred-ref; nonzero=ref!=0
        mae=np.mean(np.abs(err)); mean_ref=np.mean(ref); nmae=100*mae/mean_ref if mean_ref else np.nan
        rows.append({"center_id":center,"definition_id":definition,"months":len(g),"registry_total":int(ref.sum()),"phenotype_total":int(pred.sum()),"MAE":mae,"nMAE_percent":nmae,"RMSE":np.sqrt(np.mean(err**2)),"MAPE_percent":100*np.mean(np.abs(err[nonzero])/ref[nonzero]) if nonzero.any() else np.nan,"mean_signed_error":np.mean(err),"count_ratio":pred.sum()/ref.sum() if ref.sum() else np.nan,"pearson_r":np.corrcoef(pred,ref)[0,1] if len(pred)>1 and np.std(pred)>0 and np.std(ref)>0 else np.nan,"lin_CCC":lin_ccc(pred,ref),"bias_direction":"over-count" if np.mean(err)>0 else "under-count" if np.mean(err)<0 else "balanced"})
    out=pd.DataFrame(rows); out["MAE_rank"]=out.groupby("center_id")["MAE"].rank(method="min",ascending=True).astype(int)
    return out.sort_values(["center_id","MAE_rank","definition_id"])

def logical_checks(df):
    wide=df.pivot_table(index=["center_id","month"],columns="definition_id",values="phenotype_count",aggfunc="sum"); rows=[]
    for subset,parent in LOGICAL_CHECKS:
        if subset not in wide.columns or parent not in wide.columns: continue
        v=wide[subset]>wide[parent]
        for (center,month),violation in v[v].items(): rows.append({"center_id":center,"month":month,"subset":subset,"parent":parent,"violation":bool(violation),"subset_count":wide.loc[(center,month),subset],"parent_count":wide.loc[(center,month),parent]})
        if not v.any(): rows.append({"center_id":"ALL","month":"ALL","subset":subset,"parent":parent,"violation":False,"subset_count":np.nan,"parent_count":np.nan})
    return pd.DataFrame(rows)

def rank_stability(metrics):
    ranks=metrics.pivot(index="definition_id",columns="center_id",values="MAE_rank"); centers=list(ranks.columns); rows=[]
    for i,c1 in enumerate(centers):
        for c2 in centers[i+1:]:
            tmp=ranks[[c1,c2]].dropna(); s=spearmanr(tmp[c1],tmp[c2]).statistic if len(tmp)>2 else np.nan; k=kendalltau(tmp[c1],tmp[c2]).statistic if len(tmp)>2 else np.nan
            top3a=set(tmp.nsmallest(3,c1).index); top3b=set(tmp.nsmallest(3,c2).index); top5a=set(tmp.nsmallest(min(5,len(tmp)),c1).index); top5b=set(tmp.nsmallest(min(5,len(tmp)),c2).index)
            rows.append({"center_pair":f"{c1} vs {c2}","definitions_compared":len(tmp),"spearman":s,"kendall":k,"top3_jaccard":len(top3a&top3b)/len(top3a|top3b),"top5_jaccard":len(top5a&top5b)/len(top5a|top5b)})
    return pd.DataFrame(rows)

def selection_policies(metrics):
    nmae=metrics.pivot(index="definition_id",columns="center_id",values="nMAE_percent").dropna(); mean_def=nmae.mean(axis=1).idxmin(); minimax_def=nmae.max(axis=1).idxmin()
    policy=pd.DataFrame([{"policy":"universal_lowest_mean_nMAE","definition_id":mean_def,"mean_nMAE":nmae.loc[mean_def].mean(),"worst_center_nMAE":nmae.loc[mean_def].max()},{"policy":"minimax_lowest_worst_center_nMAE","definition_id":minimax_def,"mean_nMAE":nmae.loc[minimax_def].mean(),"worst_center_nMAE":nmae.loc[minimax_def].max()}])
    rows=[]
    for center in nmae.columns:
        train=[c for c in nmae.columns if c!=center]; selected=nmae[train].mean(axis=1).idxmin(); local=nmae[center].idxmin()
        rows.append({"held_out_center":center,"selected_from_other_centers":selected,"held_out_nMAE":nmae.loc[selected,center],"local_optimum":local,"local_nMAE":nmae.loc[local,center],"regret_percentage_points":nmae.loc[selected,center]-nmae.loc[local,center]})
    return policy,pd.DataFrame(rows)

def bootstrap_rank_uncertainty(df,n_boot=2000,block_len=3,seed=12):
    rng=np.random.default_rng(seed); rows=[]
    for center,gcenter in df.groupby("center_id"):
        months=sorted(gcenter["month"].unique()); defs=sorted(gcenter["definition_id"].unique())
        if len(months)<block_len: continue
        lookup={(r.month,r.definition_id):(r.phenotype_count,r.registry_count) for r in gcenter.itertuples()}; ranks={d:[] for d in defs}; nmaes={d:[] for d in defs}
        for _ in range(n_boot):
            sampled=[]
            while len(sampled)<len(months):
                start=rng.integers(0,len(months)-block_len+1); sampled.extend(months[start:start+block_len])
            sampled=sampled[:len(months)]; vals=[]
            for d in defs:
                pairs=[lookup[(m,d)] for m in sampled if (m,d) in lookup]
                if not pairs: vals.append((d,np.nan)); continue
                pred=np.array([p for p,_ in pairs],float); ref=np.array([r for _,r in pairs],float); vals.append((d,100*np.mean(np.abs(pred-ref))/np.mean(ref)))
            temp=pd.DataFrame(vals,columns=["definition_id","nMAE_percent"]).dropna().sort_values("nMAE_percent")
            for rank,row in enumerate(temp.itertuples(index=False),start=1): ranks[row.definition_id].append(rank); nmaes[row.definition_id].append(row.nMAE_percent)
        for d in defs:
            arr=np.array(nmaes[d]); rnk=np.array(ranks[d]); rows.append({"center_id":center,"definition_id":d,"n_boot":len(arr),"nMAE_boot_mean":np.nanmean(arr),"nMAE_CI_low":np.nanpercentile(arr,2.5),"nMAE_CI_high":np.nanpercentile(arr,97.5),"prob_rank_first":np.mean(rnk==1),"prob_top3":np.mean(rnk<=3)})
    return pd.DataFrame(rows)

def main():
    p=argparse.ArgumentParser(); p.add_argument("--input",required=True); p.add_argument("--output-dir",required=True); p.add_argument("--bootstrap-replicates",type=int,default=2000); a=p.parse_args()
    out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True); df=pd.read_csv(a.input)
    required={"center_id","month","definition_id","phenotype_count","registry_count","definition_version"}; missing=required-set(df.columns)
    if missing: raise ValueError(f"Missing required fields: {sorted(missing)}")
    df["month"]=df["month"].astype(str); metrics=calc_metrics(df); metrics.to_csv(out/"metrics_by_center_definition.csv",index=False); logical_checks(df).to_csv(out/"logical_consistency_checks.csv",index=False); rank_stability(metrics).to_csv(out/"rank_stability.csv",index=False); policy,loco=selection_policies(metrics); policy.to_csv(out/"selection_policies.csv",index=False); loco.to_csv(out/"leave_one_center_out_regret.csv",index=False); bootstrap_rank_uncertainty(df,n_boot=a.bootstrap_replicates).to_csv(out/"bootstrap_rank_uncertainty.csv",index=False); print(f"Wrote outputs to {out}")
if __name__=="__main__": main()
