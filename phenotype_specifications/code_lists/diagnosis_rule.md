# Ischemic-stroke diagnosis rule

The study baseline candidate cohort used the following diagnosis rule:

- **ICD-9-CM:** `433.x1` and `434.x1` (the final digit `1` indicates cerebral infarction).
- **ICD-10-CM:** the `I63` cerebral-infarction family and `H34.1` central retinal artery occlusion.

Local implementations should normalize dotted/undotted code formatting before matching. The diagnosis criterion is applied within the adult inpatient/emergency-to-inpatient hospitalization cohort with length of stay >24 hours.
