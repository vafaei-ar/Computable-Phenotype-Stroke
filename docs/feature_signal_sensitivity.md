# Feature-signal diagnostics and post hoc selection sensitivity

This module extends the manuscript's aggregate benchmarking with source-signal diagnostics. It uses the existing long-format center-month-definition aggregate input (no patient-level data).

## Run

```bash
python scripts/feature_signal_sensitivity.py \
  --input data/manuscript/monthly_aggregate_counts.csv.gz \
  --output-dir outputs/feature_signal_sensitivity
```

The script produces four CSVs: nested-feature ratios, Center 1 common-window rankings, universal/minimax policy sensitivity, and leave-one-center-out regret by candidate set.

## Definitions

- `D7/D5` measures the MRI-specific signal relative to any imaging within the same ICD-defined candidate cohort.
- `D3/D1` is the analogous MRI ratio where lipid testing is also required.
- `D6/D3` is the recorded rehabilitation signal where MRI and lipid tests are required; D6 was not evaluated at Center 4.
- Center 1 alternative windows start in May 2018 and June 2018; all definitions are evaluated over the same months within each window.
- The reduced cross-site candidate set is `D0,D1,D2,D5,D8` (none has a mandatory MRI criterion). The full common set is `D0,D1,D2,D3,D4,D5,D7,D8`.

**Cautions:** These ratios are *not* independent measurements of clinical service utilization, EHR field completeness, or patient-level classification accuracy. Sparse counts can reflect practice patterns, incomplete structured capture, extraction logic, or source mapping. The sensitivity analyses were conducted after inspecting aggregate patterns. Regret values from different candidate sets are not directly comparable as gains in performance. The main manuscript's primary analyses remain unchanged.

The EHR and registry counting unit must be verified against the local source processing rules. Monthly aggregates alone do not establish whether repeated hospitalization episodes and patients are treated identically.
