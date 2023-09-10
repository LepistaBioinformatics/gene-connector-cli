import clean_base.exceptions as exc
from clean_base.either import Either, right
from pandas import DataFrame
from pandera.errors import SchemaError

from gcon.core.domain.dtos.reference_data import OptionalColumnsSchema
from gcon.settings import LOGGER

from ._dtos import ReferenceRowOptions


def validate_optional_fields(
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
