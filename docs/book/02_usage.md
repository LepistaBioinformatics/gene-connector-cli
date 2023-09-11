# USAGE 👨🏽‍💻

[◀️ Home](https://github.com/sgelias/gene-connector-cli/blob/main/README.md) | [◀️ Documentation](https://github.com/sgelias/gene-connector-cli/blob/main/docs/README.md)

___

## Data preparation

Our tool requires a simple tabular (TSV) file with the following columns:

- `identifier`: unique identifier for each specimen.
- `scientificName`: the scientific name of the organism. Its important that the column name seems exactly like this (using the [camelCase](https://en.wikipedia.org/wiki/Camel_case) syntax).
- `gene-name`: the gene column containing the accession numbers. Gene column names must be in the [kebab-case](https://en.wikipedia.org/wiki/Letter_case#Special_case_styles) syntax. Each column must be composed of two concatenated information: the source genome which the sequence was sequenced and the gene name. A comprehensive example should be found using the '`gcon info source-genomes`' command.

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

To guarantee the data integrity, we provide a simple command to validate the data file. To do so, use the following command:

```bash
gcon validate --input-table <data-file>
```

Such command will validate the data file and return a message indicating if the file is valid or not. If the file is not valid, the command will return a message indicating the error and the location of the error. Error messages are printed with a python native logging with error level, thus, the minimum logging level to be configured is `error`. In `gcon` simple configure the environment variable `LOGGING_LEVEL` to `error` or other level that includes `error` level. For example:

```bash
export LOGGING_LEVEL=error
```

In fungi taxonomy, it is common to sequencing one or more genes of the same operon with overlapping primers (like SSU, ITS, and LSU). In such cases, the same specimen will have more than one sequence for the same accession number. To deal with such cases, use the flag `--ignore-duplicates` or simple `-i`. Such flag will ignore the duplicates during validation step.

## Gene Connector execution

To execute the complete Gene Connector pipeline, use the following command:

```bash
gcon resolve \
    --input-table <data-file> \
    --output-file out
```

Such command will execute the complete pipeline and generate the output file. The above cited option `--ignore-duplicates` flag can be used here too.

## Outputs

The Gene Connector pipeline generates two files:

- `out.tsv`: the output file containing the resolved data in TSV format.
- `out.json`: the output file containing the resolved data in JSON format.

Both files are redundant, thus, the user can choose the format that best fits its needs. The JSON format is useful to be used in other tools that requires JSON as input, like web applications that uses JavaScript as programming language. The TSV format is useful to be used in other tools that requires TSV as input, like R and Python scripts.

## Example

We recommend to use the *Bipolaris* example data file provided in the `assets` repository. To do so, use the following command:

```bash
gcon resolve \
    --input-table assets/bipolaris-gophy.tsv \
    --output-file out
```

This example dataset includes duplicated records, allowing to users to test the `--ignore-duplicates` flag and see the expected results.

___

[◀️ Prev: Installation](https://github.com/sgelias/gene-connector-cli/blob/main/docs/book/01_installation.md)

[▶️ Next: Project Structure](https://github.com/sgelias/gene-connector-cli/blob/main/docs/book/03_project_structure.md)
