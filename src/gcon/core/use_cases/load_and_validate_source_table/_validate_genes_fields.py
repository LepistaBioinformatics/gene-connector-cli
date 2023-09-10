from pandas import DataFrame, Series

import gcon.core.domain.utils.exceptions as exc
from gcon.core.domain.dtos.reference_data import ReferenceData
from gcon.core.domain.utils.either import Either, right
from gcon.settings import LOGGER

from ._dtos import ReferenceRowOptions


def validate_genes_fields(
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
