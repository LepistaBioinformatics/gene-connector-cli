from typing import Any, Self
from uuid import UUID, uuid4

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

    id: UUID = field(init=False)
    identifiers: set[str] = field()
    nodes: set[Node] = field()
    scores: ConnectionScores | None = field(default=None)

    # ? ------------------------------------------------------------------------
    # ? VALIDATORS
    # ? ------------------------------------------------------------------------

    @id.default
    def _set_default_id(self) -> UUID:
        return uuid4()

    # ? ------------------------------------------------------------------------
    # ? PUBLIC INSTANCE METHODS
    # ? ------------------------------------------------------------------------

    def with_id(self, id: UUID) -> Self:
        self.id = id
        return self

    def to_dict(self) -> dict[str, UUID | list[Any] | object]:
        """Convert the connection to a dictionary.

        Returns:
            dict[str, list[str]]: The connection as a dictionary.

        """

        return {
            "id": self.id,
            "identifiers": list(self.identifiers),
            "nodes": [node.to_dict() for node in self.nodes],
            "scores": self.scores.to_dict() if self.scores else None,
        }

    def with_scores(self, scores: ConnectionScores) -> None:
        self.scores = scores
