from pathlib import Path
from uuid import uuid4

from numpy import nan
from pandas import read_csv

import gcon.core.domain.utils.exceptions as exc
from gcon.core.domain.dtos.reference_data import (
    ReferenceData,
    StandardFieldsSchema,
)
from gcon.core.domain.utils.either import Either, right
from gcon.settings import LOGGER

from ._validate_genes_fields import validate_genes_fields
from ._validate_optional_fields import validate_optional_fields
from ._validate_required_fields import validate_required_fields


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

        if (
            validation_response := validate_required_fields(
                definition_row=definition_row,
                content_rows=content_rows,
            )
        ).is_left:
            return validation_response
        del validation_response

        # ? --------------------------------------------------------------------
        # ? Pre-load definition-rows
        #
        # Optional fields
        #
        # ? --------------------------------------------------------------------

        if (
            validation_response := validate_optional_fields(
                definition_row=definition_row,
                content_rows=content_rows,
            )
        ).is_left:
            return validation_response

        optional_fields: list[str] = validation_response.value
        del validation_response

        # ? --------------------------------------------------------------------
        # ? Pre-load definition-rows
        #
        # Gene fields
        #
        # ? --------------------------------------------------------------------

        if (
            validation_response := validate_genes_fields(
                definition_row=definition_row,
                content_rows=content_rows,
                ignore_duplicates=ignore_duplicates,
            )
        ).is_left:
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
