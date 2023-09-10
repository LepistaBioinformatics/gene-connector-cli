from pandas import DataFrame
from pandera.errors import SchemaError

import gcon.core.domain.utils.exceptions as exc
from gcon.core.domain.dtos.reference_data import StandardFieldsSchema
from gcon.core.domain.utils.either import Either, right
from gcon.settings import LOGGER


def validate_required_fields(
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
