# Quarterly and two-quarter aggregation provenance

Supplementary Table S3 uses the released **monthly aggregate** phenotype and registry series. Each center/definition is evaluated at three resolutions:

- `monthly`: original admission-month counts.
- `quarterly`: calendar-quarter totals, `resample('QS').sum()`.
- `semiannual`: consecutive two-quarter totals, `resample('2QS').sum()`.

The crucial detail is the two-quarter **anchor**: Pandas `2QS` starts with the calendar-quarter boundary containing the first observed month of each input series. It does **not** always mean fixed January-June and July-December calendar halves.

| Center | First month | Two-quarter windows used |
|---|---|---|
| 1 | 2016-12 | Oct-Mar and Apr-Sep |
| 2 | 2017-01 | Jan-Jun and Jul-Dec |
| 3 | 2016-03 | Jan-Jun and Jul-Dec |
| 4 | 2023-03 | Jan-Jun and Jul-Dec |

Partial periods at the start and end of an observation window are retained. No events from other months are imputed. For each period, EHR phenotype counts and `SR` registry counts are summed separately before MAE, nMAE, RMSE, signed error, count ratio, and Pearson correlation are recomputed. MAPE excludes periods with zero registry counts.

Reproducible command:

```bash
python scripts/aggregation_sensitivity.py \
  --input data/manuscript/monthly_aggregate_counts.csv.gz \
  --output outputs/aggregation_sensitivity.csv
```

**Cross-check from the manuscript's Supplementary Table S2:** Center 1 D0 has 15 semiannual periods, MAE = 172.13, RMSE = 188.82, and Pearson r = 0.64. Recomputing all 105 S3 rows from the released monthly S2 series matches every displayed number within rounding. Replacing `2QS` with fixed calendar halves changes some reported metrics and is **not** the manuscript's original analysis.

This grouping issue does not change the primary monthly phenotype results or feature-capture sensitivity analyses.
