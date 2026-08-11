# Aggregate input data dictionary

The analysis input is a long-format CSV with one row per center-month-definition.

| Field | Required | Description |
|---|---:|---|
| `center_id` | Yes | Anonymized center identifier. |
| `month` | Yes | Admission month (`YYYY-MM`). |
| `definition_id` | Yes | `D0` through `D8`. |
| `phenotype_count` | Yes | Number of EHR-derived qualifying hospitalization records. |
| `registry_count` | Yes | Local stroke-registry benchmark count for the same month. |
| `definition_version` | Yes | Version of phenotype logic/code lists. |
| `ehr_completeness_flag` | No | Optional source completeness indicator. |
| `registry_completeness_flag` | No | Optional benchmark completeness indicator. |
| `inpatient_volume` | No | Optional denominator for secondary analyses. |
| subgroup fields | No | Optional aggregate subgroup counts. |

No patient identifiers, dates more granular than month, or patient-level registry labels are required by the central analysis.
