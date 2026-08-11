# Computable-Phenotype-Stroke

Reproducible materials for **aggregate benchmarking of computable EHR phenotypes across health systems**, with hospitalized ischemic stroke as the demonstration case.

The framework is intended for multisite settings where patient-level registry labels cannot be centralized. Each site executes the same phenotype definitions locally, aggregates counts by admission month, and shares only approved aggregate outputs. Central analysis produces a multidimensional phenotype transportability profile rather than a single score.

## What is included

- executable phenotype logic (`D0`-`D8`) and study code lists;
- documented long-format aggregate input schema;
- de-identified manuscript aggregate counts and summary outputs;
- synthetic demonstration data;
- reproducible metrics for error, bias, temporal tracking, Lin CCC, rank stability, logical consistency, universal/minimax selection, leave-one-center-out transportability regret, and moving-block bootstrap rank uncertainty; and
- disclosure/anonymity guidance.

## Repository layout

```text
data/
  input_schema.yaml
  manuscript/
  synthetic/
docs/
phenotype_specifications/
  phenotype_definitions.yaml
  code_lists/
scripts/
tests/
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python scripts/validate_input.py data/synthetic/synthetic_aggregate_counts.csv
python scripts/run_aggregate_benchmark.py \
  --input data/synthetic/synthetic_aggregate_counts.csv \
  --output-dir example_outputs
```

To reproduce the manuscript aggregate analyses from the released monthly counts:

```bash
python scripts/run_aggregate_benchmark.py \
  --input data/manuscript/monthly_aggregate_counts.csv \
  --output-dir manuscript_outputs
```

## Phenotype baseline and timing

The candidate cohort includes adults (age >=18 years) with an inpatient or emergency-to-inpatient hospitalization lasting >24 hours and an eligible ischemic-stroke ICD code. Imaging is captured from 2 days before admission through discharge; lipid/cholesterol testing and rehabilitation signals are captured during the hospitalization. See `docs/executable_phenotype_specification.md` and the code-list files for details.

## Interpretation

Aggregate benchmarking evaluates **burden agreement and transportability**, not patient-level diagnostic accuracy. It cannot estimate sensitivity, specificity, PPV, false-negative rate, or false-discovery rate, and offsetting false-positive/false-negative errors can be hidden at the count level.

Pearson correlation is used only for temporal tracking. Absolute agreement is characterized with nMAE, signed bias/count ratio, and Lin's concordance correlation coefficient.

## Institutional anonymity and disclosure

Center IDs are anonymized. Site characteristics are intentionally broad. Users should apply local small-cell disclosure rules before sharing or publishing aggregate outputs. See `docs/disclosure_and_anonymity.md`.

## Manuscript

**Aggregate benchmarking as a quality-assurance layer for multisite computable EHR phenotypes: an ischemic stroke study.**
