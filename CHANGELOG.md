## v0.3.0 (2023-05-02)

### Feat

- implements a caching strategy based on pickle-db
- implements the aceptance of accession lists in gene source codes
- implements the all in one pipeline runner to execute the full cli steps

### Fix

- remove unused print after execute the main cli case
- update the genes validation of the reference-data model
- fix the wrong calculation of the completeness indices in build-metadata-match-scores use-case

## v0.2.0 (2023-04-23)

### Feat

- implements the completeness scores calculation use-case and associated elements as dtos
- implements the metadata download and parsing and the connections object with their derivates
- initial commit

### Refactor

- move use-cases from submodules to top level modules inside use-cases module
- move gc main project folder to gcon to avoid conflict with linux internal packages
