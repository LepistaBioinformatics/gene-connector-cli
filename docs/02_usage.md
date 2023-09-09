# USAGE

[⬅️ Home](../README.md)
___

## Data preparation

Our tool requires a simple tabular (TSV) file with the following columns:

- `identifier`: unique identifier for each specimen.
- `scientificName`: the scientific name of the organism.
- `gene-name`: the gene column containing the accession numbers.

The first line of the file after the header must contains the column classifier names. Column classifier must be:

- `#gcon:defs`: Indicating that the current document is a Gene Connector definition file.
- `std`: Indicating a standard colum (see above).
- `gene`: Indicating a gene column (see above).

Example:

| identifier     | scientificName         | nuc-its     | mit-gapdh |
| -------------- | ---------------------- | ----------- | --------- |
| **#gcon:defs** | **std**                | **gene**    | **gene**  |
| BRIP 12490T    | *Bipolaris austrostipae* | KX452442  | KX452408  |

On the second line is the column classifier line. It is must important that the column classifier line is the second line of the file.

## Data validation

To do!

## Gene Connector execution

To do!

## Outputs

To do!
