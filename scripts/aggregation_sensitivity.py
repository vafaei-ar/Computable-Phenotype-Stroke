#!/usr/bin/env python3
"""Reproduce monthly, quarterly and source-anchored two-quarter aggregate agreement.

Only center/month/definition aggregate inputs are used; no patient-level data.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED = {"center_id", "month", "definition_id", "phenotype_count", "registry_count"}
GROUPS = {"monthly": "MS", "quarterly": "QS", "semiannual": "2QS"}


def evaluate(source: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED - set(source.columns)
    if missing:
        raise ValueError(f"Missing required fields: {sorted(missing)}")
    df = source.copy()
    if df[list(REQUIRED)].isna().any().any():
        raise ValueError("Required fields include missing values")
    if df.duplicated(["center_id", "month", "definition_id"]).any():
        raise ValueError("Duplicate center/month/definition rows")
    for col in ["registry_count", "phenotype_count"]:
        df[col] = pd.to_numeric(df[col], errors="raise")
        if (df[col] < 0).any():
            raise ValueError(f"Negative counts: {col}")
    df["month"] = pd.to_datetime(df["month"].astype(str), format="%Y-%m")

    out = []
    for (center, definition), g in df.groupby(["center_id", "definition_id"], sort=True):
        g = g.sort_values("month").set_index("month")
        for label, rule in GROUPS.items():
            # 2QS starts at the quarter containing the first observed month.
            # It is not necessarily Jan-Jun/Jul-Dec (Center 1 starts in Q4).
            agg = g[["registry_count", "phenotype_count"]].resample(rule).sum()
            agg = agg.dropna(subset=["registry_count", "phenotype_count"])
            r = agg["registry_count"].to_numpy(dtype=float)
            p = agg["phenotype_count"].to_numpy(dtype=float)
            e = p - r
            mae = float(np.mean(np.abs(e)))
            mean_r = float(np.mean(r))
            nz = r != 0
            corr = (
                float(np.corrcoef(r, p)[0, 1])
                if len(r) > 1 and np.std(r) > 0 and np.std(p) > 0
                else np.nan
            )
            signed = float(np.mean(e))
            out.append({
                "center_id": center,
                "aggregation": label,
                "definition_id": definition,
                "periods": len(agg),
                "MAE": mae,
                "nMAE_pct": 100 * mae / mean_r if mean_r else np.nan,
                "RMSE": float(np.sqrt(np.mean(e * e))),
                "MAPE_pct": float(100 * np.mean(np.abs(e[nz]) / r[nz]))
                if nz.any() else np.nan,
                "signed_error": signed,
                "count_ratio": float(np.sum(p) / np.sum(r)) if np.sum(r) else np.nan,
                "pearson_r": corr,
                "bias": "over-count" if signed > 0 else "under-count" if signed < 0 else "balanced",
            })
    return pd.DataFrame(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    data = pd.read_csv(
        args.input, compression="infer",
        dtype={"center_id": str, "definition_id": str, "month": str},
    )
    result = evaluate(data)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(path, index=False, float_format="%.9g")
    print(f"Wrote {len(result)} rows to {path}")


if __name__ == "__main__":
    main()
