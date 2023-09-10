import re
from functools import reduce
from operator import iconcat

from gcon.core.domain.dtos.connection import Connection
from gcon.core.domain.dtos.metadata import MetadataKey, MetadataKeyGroup


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

    group_completeness: dict[MetadataKeyGroup, bool] = {
        group: False for group in non_zero_groups
    }

    group_scores: dict[MetadataKeyGroup, int] = {
        group: 0 for group in non_zero_groups
    }

    for group in non_zero_groups:
        higher_score = 0

        for key in group.value.keys:
            metadata_key = MetadataKey(group=group, key=key)

            nodes_with_key: list[tuple[str, set[str]]] = [
                (
                    node.accession,
                    set(
                        reduce(
                            iconcat,
                            [
                                v
                                for k, v in node.metadata.qualifiers.items()
                                if k == metadata_key
                            ],
                            [],
                        )
                    ),
                )
                for node in connection.nodes
                if metadata_key in node.metadata.qualifiers.keys()
            ]

            values_shared_by_nodes: dict[str, set[str]] = dict()

            for accession, values in nodes_with_key:
                for value in values:
                    # Replace all non alphanumeric characters from string
                    # to nothing
                    value = re.sub(r"\W+", "", value).lower()

                    if value not in values_shared_by_nodes:
                        values_shared_by_nodes[value] = set()
                    values_shared_by_nodes[value].add(accession)

            if not values_shared_by_nodes:
                continue

            nodes_set_score = max(
                len(accessions) * group.value.score
                for _, accessions in values_shared_by_nodes.items()
            )

            if nodes_set_score > higher_score:
                higher_score = nodes_set_score

        if higher_score > 0:
            group_completeness[group] = True
            group_scores[group] = higher_score

    return (
        group_completeness,
        sum(group_scores.values()),
    )
