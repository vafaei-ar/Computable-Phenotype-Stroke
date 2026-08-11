# Disclosure and institutional anonymity

The workflow is designed for aggregate sharing. Sites execute phenotype logic locally and share only approved aggregate outputs.

Recommended practices:

- use anonymized center identifiers in shared analysis files;
- do not include patient identifiers or encounter identifiers;
- use month-level rather than patient-level dates;
- apply local small-cell disclosure rules before public release;
- report institutional characteristics at a deliberately broad level when site anonymity is required; and
- retain a local crosswalk between anonymized center IDs and institutions outside the public repository.

The repository does not claim formal differential privacy. Aggregate data can still create disclosure risk when cells are small.
