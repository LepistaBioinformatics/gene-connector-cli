from typing import Any

from attrs import define, field

from gcon.core.domain.dtos.node import Node
from gcon.core.domain.dtos.score import ConnectionScores


@define(kw_only=True)
class Connection:
    """Connection class.

    Attributes:
        identifiers (set[str]): The identifiers of the connection.
        nodes (set[Node]): The nodes of the connection.

    """

    # ? ------------------------------------------------------------------------
    # ? CLASS ATTRIBUTES
    # ? ------------------------------------------------------------------------

    identifiers: set[str] = field()
    nodes: set[Node] = field()
    scores: ConnectionScores | None = field(default=None)

    # ? ------------------------------------------------------------------------
    # ? PUBLIC INSTANCE METHODS
    # ? ------------------------------------------------------------------------

    def to_dict(self) -> dict[str, list[Any]]:
        """Convert the connection to a dictionary.

        Returns:
            dict[str, list[str]]: The connection as a dictionary.

        """

        return {
            "identifiers": list(self.identifiers),
            "nodes": [node.to_dict() for node in self.nodes],
        }

    def with_scores(self, scores: ConnectionScores) -> None:
        self.scores = scores
