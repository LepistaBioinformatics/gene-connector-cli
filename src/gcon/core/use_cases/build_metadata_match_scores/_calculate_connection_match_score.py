import clean_base.exceptions as exc
from clean_base.either import Either, right

from gcon.core.domain.dtos.connection import Connection
from gcon.core.domain.dtos.metadata import MetadataKeyGroup
from gcon.core.domain.dtos.score import ConnectionScores
from gcon.settings import LOGGER

from ._calculate_connection_observed_score import (
    calculate_connection_observed_score,
)


def calculate_connection_match_score(
    connection: Connection,
) -> Either[exc.UseCaseError, Connection]:
    """Calculate the match score of a connection.

    Args:
        connection (Connection): The connection to calculate the match score.

    Returns:
        Either[exc.UseCaseError, Connection]: The connection with the match
            score.

    """

    try:
        # ? --------------------------------------------------------------------
        # ? Validate input arguments
        # ? --------------------------------------------------------------------

        if not isinstance(connection, Connection):
            return exc.InvalidArgumentError(
                f"`{connection}` is not a valid instance of `{type(Connection)}`",
                logger=LOGGER,
            )()

        # ? --------------------------------------------------------------------
        # ? Calculate observed scores by group
        # ? --------------------------------------------------------------------

        non_zero_groups = [i for i in MetadataKeyGroup if i.value.score > 0]

        used_groups: dict[MetadataKeyGroup, bool]
        observed_score: int

        (
            used_groups,
            observed_score,
        ) = calculate_connection_observed_score(
            connection=connection,
            non_zero_groups=non_zero_groups,
        )

        # ? --------------------------------------------------------------------
        # ? Calculate expected score
        # ? --------------------------------------------------------------------

        expected_score = sum(
            [i.value.score * len(connection.nodes) for i in non_zero_groups]
        )

        # ? --------------------------------------------------------------------
        # ? Calculate non-zero groups score
        # ? --------------------------------------------------------------------

        non_zero_group_score = sum(
            [
                group.value.score * len(connection.nodes)
                for group, was_used in used_groups.items()
                if was_used is True
            ]
        )

        # ? --------------------------------------------------------------------
        # ? Calculate observed completeness score
        # ? --------------------------------------------------------------------

        observed_completeness_score = round(
            observed_score / expected_score,
            ndigits=2,
        )

        # ? --------------------------------------------------------------------
        # ? Calculate reachable completeness score
        # ? --------------------------------------------------------------------

        reachable_completeness_score = round(
            non_zero_group_score / expected_score,
            ndigits=2,
        )

        # ? --------------------------------------------------------------------
        # ? Update input connection with scores
        # ? --------------------------------------------------------------------

        connection.with_scores(
            scores=ConnectionScores(
                observed_completeness_score=observed_completeness_score,
                reachable_completeness_score=reachable_completeness_score,
            )
        )

        # ? --------------------------------------------------------------------
        # ? Return a positive response
        # ? --------------------------------------------------------------------

        return right(connection)

    except Exception as e:
        LOGGER.warning(connection)
        return exc.UseCaseError(e, logger=LOGGER)()
