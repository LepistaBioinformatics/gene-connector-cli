from __future__ import annotations

from attrs import field, frozen

from gcon.core.domain.dtos.metadata import Metadata


@frozen(kw_only=True)
class Node:
    """Node class.

    Attributes:
        accession (str): The accession of the node.
        metadata (Metadata): The metadata of the node.

    Methods:
        to_dict: Convert the node to a dictionary.

    """

    # ? ------------------------------------------------------------------------
    # ? CLASS ATTRIBUTES
    # ? ------------------------------------------------------------------------

    accession: str = field()
    metadata: Metadata = field()

    # ? ------------------------------------------------------------------------
    # ? LIFE CYCLE HOOK METHODS
    # ? ------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Node) and self.__hash__() == other.__hash__()

    def __hash__(self) -> int:
        return hash((self.accession, self.metadata))

    # ? ------------------------------------------------------------------------
    # ? PUBLIC INSTANCE METHODS
    # ? ------------------------------------------------------------------------

    def to_dict(self) -> dict[str, str | int]:
        return {
            "accession": self.accession,
            "metadata": self.metadata.to_dict(),
        }
