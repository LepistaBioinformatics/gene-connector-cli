from __future__ import annotations

from attrs import field, frozen

import gcon.core.domain.utils.exceptions as exc
from gcon.core.domain.dtos.metadata import (
    Metadata,
    MetadataKey,
    MetadataKeyGroup,
)
from gcon.core.domain.utils.either import Either, right
from gcon.settings import LOGGER


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
    marker: str = field()
    metadata: Metadata = field()

    # ? ------------------------------------------------------------------------
    # ? LIFE CYCLE HOOK METHODS
    # ? ------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Node) and self.__hash__() == other.__hash__()

    def __hash__(self) -> int:
        return hash(
            (self.accession, self.marker, self.metadata.qualifiers.keys())
        )

    # ? ------------------------------------------------------------------------
    # ? PUBLIC INSTANCE METHODS
    # ? ------------------------------------------------------------------------

    def to_dict(self) -> dict[str, str | int]:
        return {
            "accession": self.accession,
            "marker": self.marker,
            "metadata": self.metadata.to_dict(),
        }

    @classmethod
    def from_dict(
        cls,
        node_dict: dict[str, str | int],
    ) -> Either[exc.MappedErrors, Node]:
        required_node_keys = [
            "accession",
            "marker",
            "metadata",
        ]

        for grouped_key in required_node_keys:
            if grouped_key not in node_dict:
                return exc.InvalidArgumentError(
                    f"Unable to load JSON. Missing key: `{grouped_key}`",
                    logger=LOGGER,
                )()

        accession = node_dict.pop("accession")
        marker = node_dict.pop("marker")
        metadata = node_dict.pop("metadata")

        if not isinstance(accession, str):
            return exc.InvalidArgumentError(
                "Unable to load JSON. Accession must be a string.",
                logger=LOGGER,
            )()

        if not isinstance(marker, str):
            return exc.InvalidArgumentError(
                "Unable to load JSON. Marker must be a string.",
                logger=LOGGER,
            )()

        if not isinstance(metadata, dict):
            return exc.InvalidArgumentError(
                "Unable to load JSON. Metadata must be a dictionary.",
                logger=LOGGER,
            )()

        metadata_instance = Metadata()

        for grouped_key, value in metadata.items():
            if not isinstance(grouped_key, str):
                return exc.InvalidArgumentError(
                    "Unable to load JSON. Metadata key must be a string.",
                    logger=LOGGER,
                )()

            if not isinstance(value, list):
                return exc.InvalidArgumentError(
                    "Unable to load JSON. Metadata value must be a string.",
                    logger=LOGGER,
                )()

            splitted_key = grouped_key.split(".")

            if len(splitted_key) != 2:
                return exc.InvalidArgumentError(
                    "Unable to load JSON. Metadata key must be in the format `namespace.key`.",
                    logger=LOGGER,
                )()

            group, key = tuple(splitted_key)

            try:
                group_enum = MetadataKeyGroup[group]
            except KeyError:
                return exc.InvalidArgumentError(
                    f"Unable to load JSON. Invalid metadata key group: `{group}`.",
                    logger=LOGGER,
                )()

            if key not in group_enum.value.keys:
                return exc.InvalidArgumentError(
                    f"Unable to load JSON. Invalid metadata key: `{key}`.",
                    logger=LOGGER,
                )()

            expected_metadata_key = MetadataKey(
                group=group_enum,
                key=key,
            )

            metadata_instance.add_feature(key=key, value=value)

            if expected_metadata_key not in metadata_instance.qualifiers:
                return exc.InvalidArgumentError(
                    f"Unable to load JSON. Invalid metadata key: `{key}`.",
                    logger=LOGGER,
                )()

        return right(
            cls(
                accession=accession,
                marker=marker,
                metadata=metadata_instance,
            )
        )
