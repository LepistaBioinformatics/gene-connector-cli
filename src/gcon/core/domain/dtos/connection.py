from typing import Any, Self
from uuid import UUID, uuid3, uuid4

from attrs import define, field

from gcon.core.domain.dtos.node import Node
from gcon.core.domain.dtos.score import ConnectionScores
from gcon.settings import GCON_NAMESPACE_HASH


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
    signature: UUID = field(init=False)
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

        me = self.__update_signature()

        return {
            "id": me.id,
            "signature": me.signature,
            "identifiers": list(me.identifiers),
            "nodes": [
                node.to_dict(update_signature=False) for node in me.nodes
            ],
            "scores": me.scores.to_dict() if me.scores else None,
        }

    def with_scores(self, scores: ConnectionScores) -> None:
        self.scores = scores

    # ? ------------------------------------------------------------------------
    # ? PUBLIC INSTANCE METHODS
    # ? ------------------------------------------------------------------------

    def __update_signature(self) -> Self:
        """Update the connection signature.

        This is an internal method called before to convert the connection to a
        dictionary.

        """

        nodes_signature = "".join(
            [
                node.signature.__str__()
                for node in sorted(
                    [i.update_signature() for i in self.nodes],
                    key=lambda x: x.signature,
                )
            ]
        )

        self.signature = uuid3(
            namespace=GCON_NAMESPACE_HASH,
            name=("".join(self.identifiers) + nodes_signature),
        )

        return self
