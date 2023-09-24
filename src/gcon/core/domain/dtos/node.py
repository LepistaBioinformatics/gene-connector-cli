from typing import Self
from uuid import UUID, uuid3

import clean_base.exceptions as exc
from attrs import define, field
from clean_base.either import Either, right

from gcon.core.domain.dtos.metadata import (
    Metadata,
    MetadataKey,
    MetadataKeyGroup,
)
from gcon.settings import GCON_NAMESPACE_HASH, LOGGER


@define(kw_only=True)
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

    signature: UUID = field(init=False)
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

    def update_signature(self) -> Self:
        """Update the node signature.

        This is an public method called before to convert the node to a
        dictionary.

        """

        dict_metadata = self.metadata.to_dict()

        self.signature = uuid3(
            namespace=GCON_NAMESPACE_HASH,
            name=(
                self.accession
                + self.marker
                + "".join(sorted(dict_metadata.keys()))
                + "".join(["".join(i) for i in sorted(dict_metadata.values())])
            ),
        )

        return self

    def to_dict(
        self,
        update_signature: bool = True,
    ) -> dict[str, str | int | UUID]:
        me = self

        if update_signature:
            me = self.update_signature()

        return {
            "signature": me.signature.__str__(),
            "accession": me.accession,
            "marker": me.marker,
            "metadata": me.metadata.to_dict(),
        }

    # ? ------------------------------------------------------------------------
    # ? PUBLIC CLASS METHODS
    # ? ------------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        node_dict: dict[str, str | int],
    ) -> Either[exc.MappedErrors, Self]:
        required_node_keys = ["signature", "accession", "marker", "metadata"]

        for grouped_key in required_node_keys:
            if grouped_key not in node_dict:
                return exc.DadaTransferObjectError(
                    f"Unable to load JSON. Missing key: `{grouped_key}`",
                    logger=LOGGER,
                )()

        accession = node_dict.pop("accession")
        marker = node_dict.pop("marker")
        metadata = node_dict.pop("metadata")

        if not isinstance(accession, str):
            return exc.DadaTransferObjectError(
                "Unable to load JSON. Accession must be a string.",
                logger=LOGGER,
            )()

        if not isinstance(marker, str):
            return exc.DadaTransferObjectError(
                "Unable to load JSON. Marker must be a string.",
                logger=LOGGER,
            )()

        if not isinstance(metadata, dict):
            return exc.DadaTransferObjectError(
                "Unable to load JSON. Metadata must be a dictionary.",
                logger=LOGGER,
            )()

        metadata_instance = Metadata()

        for grouped_key, value in metadata.items():
            if not isinstance(grouped_key, str):
                return exc.DadaTransferObjectError(
                    "Unable to load JSON. Metadata key must be a string.",
                    logger=LOGGER,
                )()

            if not isinstance(value, list):
                return exc.DadaTransferObjectError(
                    "Unable to load JSON. Metadata value must be a string.",
                    logger=LOGGER,
                )()

            splitted_key = grouped_key.split(".")

            if len(splitted_key) != 2:
                return exc.DadaTransferObjectError(
                    (
                        "Unable to load JSON. Metadata key must be in the "
                        + "format `namespace.key`."
                    ),
                    logger=LOGGER,
                )()

            group, key = tuple(splitted_key)

            try:
                group_enum = MetadataKeyGroup[group]
            except KeyError:
                return exc.DadaTransferObjectError(
                    f"Unable to load JSON. Invalid metadata key group: `{group}`.",
                    logger=LOGGER,
                )()

            if key not in group_enum.value.keys:
                return exc.DadaTransferObjectError(
                    f"Unable to load JSON. Invalid metadata key: `{key}`.",
                    logger=LOGGER,
                )()

            expected_metadata_key = MetadataKey(
                group=group_enum,
                key=key,
            )

            metadata_instance.add_feature(key=key, value=value)

            if expected_metadata_key not in metadata_instance.qualifiers:
                return exc.DadaTransferObjectError(
                    f"Unable to load JSON. Invalid metadata key: `{key}`.",
                    logger=LOGGER,
                )()

        return right(
            cls(
                accession=accession,
                marker=marker,
                metadata=metadata_instance,
            ).update_signature()
        )
