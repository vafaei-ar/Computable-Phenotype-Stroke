# Historical Center 1 extraction and monthly count provenance

This document describes the **historical implementation that generated the manuscript's Center 1 monthly counts**. It is deliberately separate from the common D0-D8 clinical rule set. Participating investigators discussed a common phenotype protocol and implemented it locally; their extraction scripts were not centrally collected.

## EHR numerator (D0-D8)

The original Center 1 notebook `phd_rec.ipynb` (local source, not distributed with patient-level input files) generated `outcomes/PS_conditions.csv` as follows:

1. The source pathway identified ischemic-stroke diagnosis records linked to inpatient or emergency-inpatient encounters. Eligibility included a calendar-day crossing rule; it was not a strict test of more than 24 elapsed hours.
2. The source cohort's overnight qualification identified patients, after which the original logic could retain a different qualifying stroke encounter for the same person. Procedure availability and the ordering of cohort construction affected the historical record set.
3. It constructed CT, MRI, lipid, and rehabilitation flags. Imaging was present with a same-encounter code **or** a patient-history procedure dated within an absolute two-day interval of admission. Lipid and rehabilitation evidence were encounter-linked. This is not the same as a single one-sided two-day-before-admission-through-discharge window.
4. It selected the first retained stroke encounter per `PATID` by admission date **before** applying the local facility restriction, then counted definition-positive unique patients by admission month. Later admissions for the same patient did not contribute additional index events.
5. No separate age-at-stroke >=18 filter was explicitly applied in the traced Center 1 monthly-count construction.

These points preserve historical provenance; they are **not recommendations for a new stroke phenotype implementation**. In particular, the shared study specification still describes intended adult and length-of-stay criteria. The historical implementation should not be silently altered merely to conform to its prose description.

## Registry denominator (SR)

Notebook cell 102 read the historical `Super Universe_2024.csv` stroke registry snapshot, retained `Type == 'Ischemic'` and `Diagnosis == 'Primary'`, then selected the earliest recorded month per `MRN`. Cell 103 assigned the monthly MRN counts to `SR` and wrote `outcomes/PS_conditions.csv`.

Thus, **both Center 1 count series use a first-event-per-person convention**, though the registry and EHR eligibility pathways remain distinct.

## Exact reproducibility checkpoint

A separate raw-data refactor reproduced all **85 Center 1 months (December 2016-December 2023)** and the historical D0-D8 counts exactly, using the protected source tables locally. Reported totals: D0 6,582; D1 4,953; D2 5,872; D3 4,320; D4 4,821; D5 6,192; D6 3,388; D7 5,016; D8 4,189. The `SR` reference totals 4,000 across these months.

Technical provenance and regression tests for that work are available separately in the `reproducible-analysis-pipeline` branch of [vafaei-ar/stroke-phenotype](https://github.com/vafaei-ar/stroke-phenotype/tree/reproducible-analysis-pipeline), including `docs/legacy_provenance.md`. The restricted source data and full historical notebook are not posted publicly.

## Interpretation and scope

The public repository here reproduces **aggregate diagnostics from the released monthly tables**, not the complete private EHR and registry extraction. The same D0-D8 logical definition can have site-specific implementation mappings; apparent differences in feature counts may reflect clinical use, capture, or local mapping. This document does not imply that other centers' implementations were incorrect.
