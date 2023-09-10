import clean_base.exceptions as exc
from clean_base.either import Either, right

from gcon.core.domain.dtos.reference_data import ReferenceData
from gcon.settings import LOGGER

from ._calculate_connection_match_score import calculate_connection_match_score


def build_metadata_match_scores(
    reference_data: ReferenceData,
) -> Either[exc.MappedErrors, ReferenceData]:
    """Calculate the match score of the metadata of a reference data.

    Args:
        reference_data (ReferenceData): The reference data to calculate the
            match scores.

    Returns:
        Either[exc.MappedErrors, ReferenceData]: A positive response with the
            reference data with the calculated match scores or a negative
            response with the errors.

    """

    try:
        # ? --------------------------------------------------------------------
        # ? Validate input arguments
        # ? --------------------------------------------------------------------

        if not isinstance(reference_data, ReferenceData):
            return exc.InvalidArgumentError(
                f"`{reference_data}` is not a valid instance of `{type(ReferenceData)}`",
                logger=LOGGER,
            )()

        if len(reference_data.connections) != reference_data.data.shape[0]:
            return exc.InvalidArgumentError(
                "reference data doe's not match connections length",
                logger=LOGGER,
            )()

        # ? --------------------------------------------------------------------
        # ? Calculate match scores by row
        # ? --------------------------------------------------------------------

        for index, connection in enumerate(reference_data.connections):
            calculation_response_either = calculate_connection_match_score(
                connection=connection,
            )

            if calculation_response_either.is_left:
                return calculation_response_either

            reference_data.connections[index].with_scores(
                scores=calculation_response_either.value.scores
            )

        # ? --------------------------------------------------------------------
        # ? Return a positive response
        # ? --------------------------------------------------------------------

        return right(reference_data)

    except Exception as e:
        return exc.UseCaseError(e, logger=LOGGER)()
