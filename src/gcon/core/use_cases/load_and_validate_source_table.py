from enum import Enum
from pathlib import Path
from uuid import uuid4
from numpy import nan

from pandas import DataFrame, Series, read_csv
from pandera.errors import SchemaError

import gcon.core.domain.utils.exceptions as exc
from gcon.core.domain.dtos.reference_data import (
    OptionalColumnsSchema,
    ReferenceData,
    StandardFieldsSchema,
)
from gcon.core.domain.utils.either import Either, right
from gcon.settings import LOGGER


class ReferenceRowOptions(Enum):
    IDENTIFIER = "#gcon:defs"
    STANDARD = "std"
    OPTIONAL = "opt"
    GENE = "gene"


def load_and_validate_source_table(
    source_table_path: Path,
    ignore_duplicates: bool = False,
) -> Either[exc.UseCaseError, ReferenceData]:
    """Load and validate source table

    Args:
        source_table_path (Path): Path to source table file.

    Returns:
        Either[exc.UseCaseError, ReferenceData]: Either a UseCaseError or a
            `ReferenceData` object.

    Raises:
        exc.UseCaseError: If the source table file is not found.

    """

    def format_gene_field_as_list(value: str) -> list[str]:
        if value is nan:
            return []

        return [i.strip() for i in value.split(",")] if value else []

    try:
        # ? --------------------------------------------------------------------
        # ? Validate entry params
        # ? --------------------------------------------------------------------

        if not source_table_path.exists():
            return exc.InvalidArgumentError(
                f"Source table file not found: {source_table_path}",
                logger=LOGGER,
            )()

        # ? --------------------------------------------------------------------
        # ? Load source data
        # ? --------------------------------------------------------------------

        definition_row = read_csv(source_table_path, sep="\t", nrows=1)
        content_rows = read_csv(source_table_path, sep="\t", skiprows=1)
        content_rows.columns = definition_row.columns

        # ? --------------------------------------------------------------------
        # ? Pre-load definition-rows
        #
        # Required fields
        #
        # ? --------------------------------------------------------------------

        validation_response = __validate_required_fields(
            definition_row=definition_row,
            content_rows=content_rows,
        )

        if validation_response.is_left:
            return validation_response
        del validation_response

        # ? --------------------------------------------------------------------
        # ? Pre-load definition-rows
        #
        # Optional fields
        #
        # ? --------------------------------------------------------------------

        validation_response = __validate_optional_fields(
            definition_row=definition_row,
            content_rows=content_rows,
        )

        if validation_response.is_left:
            return validation_response

        optional_fields: list[str] = validation_response.value
        del validation_response

        # ? --------------------------------------------------------------------
        # ? Pre-load definition-rows
        #
        # Gene fields
        #
        # ? --------------------------------------------------------------------

        validation_response = __validate_genes_fields(
            definition_row=definition_row,
            content_rows=content_rows,
            ignore_duplicates=ignore_duplicates,
        )

        if validation_response.is_left:
            return validation_response

        gene_fields: list[str] = validation_response.value
        del validation_response

        # ? --------------------------------------------------------------------
        # ? Return a positive response
        # ? --------------------------------------------------------------------

        data = content_rows[
            [
                StandardFieldsSchema.identifier,
                StandardFieldsSchema.sci_name,
                *optional_fields,
                *gene_fields,
            ]
        ]

        for gene in gene_fields:
            data[gene] = data[gene].apply(
                lambda x: format_gene_field_as_list(x)
            )

        data["uuid"] = [uuid4() for _ in range(len(data.index))]

        return right(
            ReferenceData(
                data=data,
                optional_fields=optional_fields,
                gene_fields=gene_fields,
            )
        )

    except Exception as e:
        return exc.UseCaseError(e, logger=LOGGER)()


def __validate_required_fields(
    definition_row: DataFrame,
    content_rows: DataFrame,
) -> Either[exc.UseCaseError, None]:
    """Validate required fields in source table

    Args:
        definition_row (DataFrame): The definition row of the source table

    Returns:
        Either[exc.UseCaseError, None]: Either a UseCaseError or None

    Raises:
        exc.UseCaseError: If unable to find definition row or identifier column

    """

    if definition_row.shape[0] != 1:
        return exc.UseCaseError(
            "Unable to find definition row in source table",
            logger=LOGGER,
        )()

    if StandardFieldsSchema.identifier not in definition_row.columns:
        return exc.UseCaseError(
            "Unable to find identifier column in source table",
            logger=LOGGER,
        )()

    if StandardFieldsSchema.sci_name not in definition_row.columns:
        return exc.UseCaseError(
            "Unable to find scientific name column in source table",
            logger=LOGGER,
        )()

    try:
        StandardFieldsSchema.validate(
            content_rows[
                [StandardFieldsSchema.identifier, StandardFieldsSchema.sci_name]
            ]
        )
    except SchemaError as e:
        return exc.UseCaseError(e, logger=LOGGER)()

    return right(None)


def __validate_optional_fields(
    definition_row: DataFrame,
    content_rows: DataFrame,
) -> Either[exc.UseCaseError, list[str]]:
    """Validates the optional fields in the source table

    Args:
        definition_row (DataFrame): A pandas dataframe containing the definition
            row of the source table
        content_rows (DataFrame): A pandas dataframe containing the content rows
            of the source table

    Returns:
        Either[exc.UseCaseError, list[str]]: A list of optional fields or an
            error

    Raises:
        exc.UseCaseError: If unable to parse literature field

    """

    optional_fields = list(
        definition_row[
            definition_row.columns[
                definition_row.where(
                    definition_row == ReferenceRowOptions.OPTIONAL.value,
                )
                .any()
                .values
            ]
        ].columns
    )

    if len(optional_fields) == 0:
        return right(optional_fields)

    try:
        OptionalColumnsSchema.validate(content_rows[optional_fields])
    except SchemaError as e:
        return exc.UseCaseError(e, logger=LOGGER)()

    return right(optional_fields)


def __validate_genes_fields(
    definition_row: DataFrame,
    content_rows: DataFrame,
    ignore_duplicates: bool = False,
) -> Either[exc.UseCaseError, list[str]]:
    """Validates the gene fields in the source table

    Args:
        definition_row (DataFrame): A pandas dataframe containing the definition
            row of the source table
        content_rows (DataFrame): A pandas dataframe containing the content rows
            of the source table

    Returns:
        Either[exc.UseCaseError, list[str]]: A list of gene fields or an error
            if the validation fails

    Raises:
        exc.UseCaseError: If the validation fails

    """

    def get_single_gene_duplications(
        col_data: Series,
    ) -> tuple[list[str], list[str]]:
        """Returns a list of duplicated gene names

        Args:
            col_data (Series): A pandas series containing the gene names

        Returns:
            tuple[list[str], list[str]]: A tuple containing a list of duplicated
                gene names and a list of unique accession numbers

        """

        unique_accessions = col_data.value_counts().index.tolist()
        duplicated_accessions = col_data.value_counts()[
            col_data.value_counts() > 1
        ].index.tolist()

        return (unique_accessions, duplicated_accessions)

    gene_fields = list(
        definition_row[
            definition_row.columns[
                definition_row.where(
                    definition_row == ReferenceRowOptions.GENE.value,
                )
                .any()
                .values
            ]
        ].columns
    )

    inter_genic_unique_accessions: list[str] = list()

    for gene in gene_fields:
        gene_parts = gene.split("-")

        if len(gene_parts) != 2:
            return exc.UseCaseError(
                f"Invalid gene name: {gene}",
                logger=LOGGER,
            )()

        location: str
        name: str
        location, name = gene_parts

        if not all(
            [
                all([i.isalpha() for i in location]),
                all([i.isalnum() for i in name]),
                len(location) == 3,
            ]
        ):
            return exc.UseCaseError(
                f"Invalid gene marker name: {gene}",
                logger=LOGGER,
            )()

        (uniques, duplicates) = get_single_gene_duplications(
            col_data=content_rows[gene]
        )

        if len(duplicates) > 0:
            return exc.UseCaseError(
                f"Duplicate gene marker names found in `{gene}`: {', '.join(duplicates)}",
                logger=LOGGER,
            )()

        for unique in uniques:
            if (
                unique in inter_genic_unique_accessions
                and ignore_duplicates is False
            ):
                return exc.UseCaseError(
                    f"Duplicate gene marker name found in `{gene}`: {unique}",
                    logger=LOGGER,
                )()

        inter_genic_unique_accessions.extend(uniques)

    ReferenceData.build_genes_schema_from_list(
        genes=gene_fields,
    ).validate(content_rows[gene_fields])

    return right(gene_fields)
