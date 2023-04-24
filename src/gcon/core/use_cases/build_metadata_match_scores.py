import gcon.core.domain.utils.exceptions as exc
from gcon.core.domain.dtos.connection import Connection
from gcon.core.domain.dtos.metadata import MetadataKeyGroup
from gcon.core.domain.dtos.reference_data import ReferenceData
from gcon.core.domain.dtos.score import ConnectionScores
from gcon.core.domain.utils.either import Either, right
from gcon.settings import LOGGER


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
            calculation_response_either = __calculate_connection_match_score(
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


def __calculate_connection_match_score(
    connection: Connection,
) -> Either[exc.UseCaseError, Connection]:
    """Calculate the match score of a connection.

    Args:
        connection (Connection): The connection to calculate the match score.

    Returns:
        Either[exc.UseCaseError, Connection]: The connection with the match
            score.

    """

    def calculate_connection_observed_score(
        connection: Connection,
        non_zero_groups: list[MetadataKeyGroup],
    ) -> tuple[dict[MetadataKeyGroup, bool], int]:
        """Calculate the observed score of a connection.

        Args:
            connection (Connection): The connection to calculate the observed
                score.
            non_zero_groups (list[MetadataKeyGroup]): The non zero groups to
                calculate the score.

        Returns:
            tuple[dict[MetadataKeyGroup, bool], int]: The completeness of the
                groups and the observed score.

        """

        nodes_scores: dict[str, dict[MetadataKeyGroup, int]] = dict()

        nodes_completeness: dict[MetadataKeyGroup, bool] = {
            group: False for group in non_zero_groups
        }

        """ for group in non_zero_groups:
            unique_metadata_keys: set[MetadataKey] = set()

            for node in connection.nodes:
                unique_metadata_keys.update(node.metadata.qualifiers.keys())

            print(unique_metadata_keys) """

        for node in connection.nodes:
            also_processed_groups: list[MetadataKeyGroup] = list()

            groups_scores: dict[MetadataKeyGroup, int] = {
                group: 0 for group in non_zero_groups
            }

            for key in node.metadata.qualifiers.keys():
                if (
                    key.group not in also_processed_groups
                    and key.group in non_zero_groups
                ):
                    also_processed_groups.append(key.group)
                    groups_scores[key.group] += key.group.value.score
                    nodes_completeness[key.group] = True

            nodes_scores.update({node.accession: groups_scores})

        return (
            nodes_completeness,
            sum(
                [
                    sum([score for score in group_scores.values()])
                    for group_scores in nodes_scores.values()
                ]
            ),
        )

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
        return exc.UseCaseError(e, logger=LOGGER)()
