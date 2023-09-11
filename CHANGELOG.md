## v0.6.3 (2023-09-10)

## v0.6.2 (2023-09-10)

## v0.6.1 (2023-09-10)

## v0.6.0 (2023-09-10)

### Feat

- implements the validate commad to check input table before run gcon pipeline

## v0.5.0 (2023-09-10)

### Feat

- include a feature that allow user to print examples from gene headers

### Fix

- move left return on find duplicate accession numbers to the last step of the genes validations to allow the pipeline to validate all records before stop pipeline

### Refactor

- replace native domain utils to use clean-base dependencies instead

## v0.4.5 (2023-09-10)

### Fix

- fix source-data validation to check all records before return an duplication error

## v0.4.4 (2023-09-10)

### Refactor

- place use-cases to dedicated sub-module folders to turn better the module organization

## v0.4.3 (2023-09-09)

## v0.4.0 (2023-05-13)

### Feat

- update the caching strategy and create a final method to generate a compiled table of all populated data
- upgrade pickledb storage
- upgrade the main pipeline execution logs to be more informative and human friendly

### Fix

- upgrade project to include the input data partially at the output data
- move the current user email checking to the use case that perform the genbank data fetching instead of the settings file

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
