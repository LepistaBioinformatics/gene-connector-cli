import clean_base.exceptions as exc
from clean_base.either import Either, right

from gcon.core.domain.dtos.metadata import MetadataKeyGroup
from gcon.core.domain.dtos.node import Node


def collect_unique_identifiers(
    nodes: list[Node],
) -> Either[exc.UseCaseError, set[str]]:
    """Collect unique identifiers from a list of nodes.

    Args:
        nodes (list[Node]): List of nodes.

    Returns:
        Either[exc.UseCaseError, set[str]]: Either a UseCaseError or a set of
            unique identifiers.

    Raises:
        exc.UseCaseError: If the metadata source is not available.

    """

    identifiers: list[str] = list()

    for node in nodes:
        specimen_keys = [
            qualifier
            for qualifier in node.metadata.qualifiers.keys()
            if qualifier.group == MetadataKeyGroup.SPECIMEN
        ]

        if len(specimen_keys) == 0:
            continue

        for qualifier in specimen_keys:
            identifiers.extend(node.metadata.qualifiers.get(qualifier))

    return right(set(identifiers))
