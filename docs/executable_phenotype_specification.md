# Executable phenotype specification

## Baseline cohort

Each candidate definition starts from hospitalized adults (age >=18 years) with an inpatient or emergency-to-inpatient encounter lasting more than 24 hours and an eligible ischemic-stroke diagnosis code. The study diagnosis families are ICD-9-CM 433.x1 and 434.x1 and ICD-10-CM I63 family and H34.1.

## Feature windows

- **CT/MRI:** CPT-coded head CT or brain MRI from 2 days before admission through the end of the index hospitalization.
- **Lipid laboratory signal:** qualifying LOINC-coded lipid/cholesterol testing during the index hospitalization.
- **Rehabilitation signal:** qualifying physical, occupational, or speech rehabilitation CPT-coded assessment/service during the index hospitalization.

## Candidate definitions

| ID | Rule |
|---|---|
| D0 | baseline only |
| D1 | baseline AND (CT OR MRI) AND lipid |
| D2 | baseline AND (CT OR MRI) AND (lipid OR rehabilitation) |
| D3 | baseline AND MRI AND lipid |
| D4 | baseline AND MRI AND (lipid OR rehabilitation) |
| D5 | baseline AND (CT OR MRI) |
| D6 | baseline AND MRI AND lipid AND rehabilitation |
| D7 | baseline AND MRI |
| D8 | baseline AND CT AND lipid |

## Episode handling

The counted unit is an eligible inpatient hospitalization record after site-specific source-row deduplication. Distinct readmission hospitalization episodes are retained as separate events.

## Code lists

The code-list CSV files in `phenotype_specifications/code_lists/` were extracted from the phenotype-development manuscript materials used for the study. Local deployments should verify source-system mapping and code availability before execution.

## Aggregate export

After local phenotype execution, convert monthly counts to the long-format schema in `data/input_schema.yaml` and run `scripts/run_aggregate_benchmark.py`.
