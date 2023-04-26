from __future__ import annotations

from enum import Enum
from hashlib import md5
from typing import Self

from attrs import define, field, frozen

from gcon.settings import LOGGER


@frozen(kw_only=True)
class MetadataGroupUnit:
    """Metadata group unit class."""

    # ? ------------------------------------------------------------------------
    # ? CLASS ATTRIBUTES
    # ? ------------------------------------------------------------------------

    description: str = field()
    keys: list[str] = field()
    score: int = field()


class MetadataKeyGroup(Enum):
    """Metadata key group enum class.

    Methods:
        set_key_group: Set the key group given the attribute key.
        default: Default key group.

    """

    # ? ------------------------------------------------------------------------
    # ? CLASS ATTRIBUTES
    # ? ------------------------------------------------------------------------

    SPECIMEN = MetadataGroupUnit(
        description=(
            "Any key that allows the unique distinction of the specimen along "
            + "the species samples."
        ),
        score=8,
        keys=[
            "bio_material",
            "clone",
            "culture_collection",
            "isolate",
            "specimen_voucher",
            "strain",
            "subclone",
            "substrain",
        ],
    )

    TAXONOMY = MetadataGroupUnit(
        description="Not also mapped keys.",
        score=5,
        keys=[
            "biovar",
            "biotype",
            "breed",
            "cultivar",
            "genotype",
            "haplogroup",
            "haplotype",
            "serogroup",
            "serotype",
            "serovar",
            "variety",
            "pathovar",
            "pop_variant",
            "organism",
            "type_material",
            "ecotype",
            "forma",
            "forma_specialis",
        ],
    )

    HOST_SUBSTRATE = MetadataGroupUnit(
        description="Keys related to host affinity or substrate preference.",
        score=3,
        keys=[
            "host",
            "isolation_source",
        ],
    )

    TIME_REFERENCES = MetadataGroupUnit(
        description="Geographic location related keys.",
        score=2,
        keys=[
            "collection_date",
        ],
    )

    GEO_REFERENCES = MetadataGroupUnit(
        description="Geographic location related keys.",
        score=2,
        keys=[
            "altitude",
            "country",
            "isolation",
            "lat_lon",
        ],
    )

    ASSAY = MetadataGroupUnit(
        description=(
            "Keys related to molecular techniques, e.g. DNA extraction, "
            + "sequencing primers, extracted molecule, and others."
        ),
        score=0,
        keys=[
            "cell_line",
            "cell_type",
            "dev_stage",
            "fwd_primer_name",
            "fwd_primer_seq",
            "lab_host",
            "mol_type",
            "pcr_primers",
            "rev_primer_name",
            "rev_primer_seq",
            "segment",
            "tissue_lib",
            "tissue_type",
            "type",
            "subtype",
        ],
    )

    EXTERNAL_LINKS = MetadataGroupUnit(
        description="External database links.",
        score=0,
        keys=[
            "db_xref",
        ],
    )

    ACTORS = MetadataGroupUnit(
        description="Not also mapped keys.",
        score=0,
        keys=[
            "authority",
            "collected_by",
            "identified_by",
        ],
    )

    OTHER = MetadataGroupUnit(
        description="Not also mapped keys.",
        score=0,
        keys=[
            "note",
            "sex",
        ],
    )

    # ? ------------------------------------------------------------------------
    # ? LIFE CYCLE HOOK METHODS
    # ? ------------------------------------------------------------------------

    def __str__(self) -> str:
        return f"{self.name} ({self.value.score})"

    # ? ------------------------------------------------------------------------
    # ? CLASS METHODS
    # ? ------------------------------------------------------------------------

    @classmethod
    def default(cls) -> Self:
        return cls.OTHER  # type: ignore

    @classmethod
    def set_key_group(cls, key: str) -> Self:
        """Set the group for a given key.

        Args:
            key (str): The key to be set.

        Returns:
            Self: The group with key belongs.

        """

        key = key.lower()

        for group in cls:
            if key in [i.lower() for i in group.value.keys]:
                return group

        LOGGER.warning(
            f"Key `{key}` not already classified. Default value (`OTHER`) used"
        )

        return cls.default()

    @classmethod
    def self_validate(self) -> None:
        """Self validate the enum class.

        Description:
            This method is used to validate the enum class. It checks if the
            enum class is valid, i.e. if the enum class has the correct
            attributes and if the attributes are valid.

            IMPORTANT: This method exists to avoid miss-updates in the enum
            class. Thus, be careful when updating these method.

        Raises:
            ValueError: If the group is not valid.

        """

        global_unique_keys: list[str] = []

        for group in self:
            if not isinstance(group.value, MetadataGroupUnit):
                raise ValueError(
                    f"Group `{group.name}` is not a valid `MetadataGroupUnit`"
                )

            if not isinstance(group.value.description, str):
                raise ValueError(
                    f"Group `{group.name}` description is not a valid `str`"
                )

            if not isinstance(group.value.keys, list):
                raise ValueError(
                    f"Group `{group.name}` keys is not a valid `list`"
                )

            if not isinstance(group.value.score, int):
                raise ValueError(
                    f"Group `{group.name}` score is not a valid `int`"
                )

            for key in group.value.keys:
                if not isinstance(key, str):
                    raise ValueError(
                        f"Group `{group.name}` key `{key}` is not a valid `str`"
                    )

                if key in global_unique_keys:
                    raise ValueError(
                        f"Group `{group.name}` key `{key}` is not unique"
                    )

                global_unique_keys.append(key)


@frozen(kw_only=True)
class MetadataKey:
    """Metadata key class.

    Attributes:
        group (MetadataKeyGroup): The group of the key.
        key (str | int): The key.

    """

    # ? ------------------------------------------------------------------------
    # ? CLASS ATTRIBUTES
    # ? ------------------------------------------------------------------------

    group: MetadataKeyGroup = field()
    key: str | int = field()

    # ? ------------------------------------------------------------------------
    # ? LIFE CYCLE HOOK METHODS
    # ? ------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, MetadataKey)
            and self.__hash__() == other.__hash__()
        )

    def __hash__(self) -> int:
        return int(
            md5((self.group.name + str(self.key)).encode()).hexdigest(),
            16,
        )

    def __str__(self) -> str:
        return f"{self.group.name}: {self.key}"


@define(kw_only=True)
class Metadata:
    """Metadata class.

    Attributes:
        qualifiers (dict[MetadataKey, str | int]): The metadata qualifiers.

    Methods:
        add_feature: Add a new feature to the metadata.

    """

    # ? ------------------------------------------------------------------------
    # ? CLASS ATTRIBUTES
    # ? ------------------------------------------------------------------------

    qualifiers: dict[MetadataKey, list[str | int]] = field(init=False)

    # ? ------------------------------------------------------------------------
    # ? VALIDATORS AND DEFAULTS
    # ? ------------------------------------------------------------------------

    @qualifiers.default
    def _set_default_qualifier(self) -> dict[MetadataKey, str]:
        return dict()

    # ? ------------------------------------------------------------------------
    # ? LIFE CYCLE HOOK METHODS
    # ? ------------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Metadata) and self.__hash__() == other.__hash__()
        )

    def __hash__(self) -> int:
        return int(md5(str(self.qualifiers).encode()).hexdigest(), 16)

    """ def __str__(self) -> str:
        return str(self.to_dict()) """

    # ? ------------------------------------------------------------------------
    # ? PUBLIC INSTANCE METHODS
    # ? ------------------------------------------------------------------------

    def to_dict(self) -> dict[str, list[str | int]]:
        """Convert the metadata to a dictionary.

        Returns:
            dict[str, list[str | int]]: The metadata as a dictionary.

        """

        return {
            f"{metadata_key.group.name}.{metadata_key.key}": value
            for metadata_key, value in self.qualifiers.items()
        }

    def add_feature(self, key: str, value: list[str | int]) -> Self:
        """Add a new feature to the metadata.

        Args:
            key (str): The key of the feature.
            value (str | int): The value of the feature.

        Returns:
            Self: The metadata with the new feature.

        """

        key = key.lower()

        self.qualifiers.update(
            {
                MetadataKey(
                    group=MetadataKeyGroup.set_key_group(key),
                    key=key,
                ): value
            }
        )

        return self
