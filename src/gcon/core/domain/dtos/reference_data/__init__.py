from json import load
from pathlib import Path
from typing import Any, Self

from attrs import field, frozen
from pandas import DataFrame
from pandera import DataFrameSchema
from pandera.errors import SchemaError

import gcon.core.domain.utils.exceptions as exc
from gcon.core.domain.dtos.connection import Connection
from gcon.core.domain.dtos.metadata import (
    Metadata,
    MetadataKey,
    MetadataKeyGroup,
)
from gcon.core.domain.dtos.node import Node
from gcon.core.domain.dtos.score import ConnectionScores
from gcon.core.domain.utils.either import Either, right
from gcon.settings import LOGGER

from .schemas import (
    GeneColumnSchema,
    OptionalColumnsSchema,
    StandardFieldsSchema,
)


@frozen(kw_only=True)
class ReferenceData:
    """ReferenceData class.

    Attributes:
        data (DataFrame): The data table content.
        optional_fields (list[str]): A list of optional fields present in data.
        gene_fields (list[str]): A list of gene fields present in data.
        connections (list[Connection]): A list of connections present in data.

    Methods:
        with_connections: Add a list of connections to the reference data.
        to_dict: Convert the reference data to a dictionary.

    """

    # ? ------------------------------------------------------------------------
    # ? CLASS ATTRIBUTES
    # ? ------------------------------------------------------------------------

    # The data table content
    data: DataFrame = field()

    # A list of optional fields present in data
    optional_fields: list[str] = field(default=list())

    # A list of gene fields present in data
    gene_fields: list[str] = field(default=list())

    # A list of connections present in data
    connections: list[Connection] = field(init=False)

    # ? ------------------------------------------------------------------------
    # ? VALIDATORS AND DEFAULTS
    # ? ------------------------------------------------------------------------

    @connections.default
    def _set_default_connections(self) -> list[Connection]:
        return list()

    # ? ------------------------------------------------------------------------
    # ? PUBLIC INSTANCE METHODS
    # ? ------------------------------------------------------------------------

    def with_connections(
        self,
        connections: list[Connection],
    ) -> None:
        """Add a list of connections to the reference data.

        Args:
            connections (list[Connection]): The list of connections to add.

        """

        self.connections.extend(connections)

    def get_genes_schema(self) -> DataFrameSchema:
        """Get the genes schema.

        Returns:
            dict[str, Column]: The genes schema.

        """

        return self.build_genes_schema_from_list(self.gene_fields)

    def to_dict(self) -> dict[str, Any]:
        """Convert the reference data to a dictionary.

        Returns:
            dict[str, list[dict[str, list[str]]]]: The reference data as a
                dictionary.

        """

        return {
            "data": self.data.to_dict(orient="records"),
            "optional_fields": self.optional_fields,
            "gene_fields": self.gene_fields,
            "connections": [
                connection.to_dict() for connection in self.connections
            ],
        }

    # ? ------------------------------------------------------------------------
    # ? PUBLIC CLASS METHODS
    # ? ------------------------------------------------------------------------

    @staticmethod
    def build_genes_schema_from_list(
        genes: list[str],
    ) -> DataFrameSchema:
        """Build a genes schema from a list of genes.

        Args:
            genes (list[str]): The list of genes.

        Returns:
            dict[str, Column]: The genes schema.

        """

        col, pattern, attrs = GeneColumnSchema

        return DataFrameSchema(
            {pattern: col(**attrs, name=gene) for gene in genes},  # type: ignore
            unique_column_names=True,
            coerce=True,
        )

    @classmethod
    def from_json(
        cls,
        json_path: Path,
    ) -> Either[exc.MappedErrors, Self]:
        """Create a reference data from a JSON file.

        Args:
            json_path (Path): The path to the JSON file.

        Returns:
            Either[exc.MappedErrors, Self]: The reference data or a list of
                errors.

        """

        try:
            # ? ----------------------------------------------------------------
            # ? Validate input arguments
            # ? ----------------------------------------------------------------

            if json_path.is_file() is False:
                return exc.InvalidArgumentError(
                    f"Invalid file path: `{json_path}`",
                    logger=LOGGER,
                )()

            # ? ----------------------------------------------------------------
            # ? Read JSON file
            # ? ----------------------------------------------------------------

            required_keys = [
                "data",
                "optional_fields",
                "gene_fields",
                "connections",
            ]

            content: dict[str, Any]

            with json_path.open("r") as f:
                content = load(f)

            for grouped_key in required_keys:
                if grouped_key not in content:
                    return exc.InvalidArgumentError(
                        f"Unable to load JSON. Missing key: `{grouped_key}`",
                        logger=LOGGER,
                    )()

            # ? ----------------------------------------------------------------
            # ? Load connections
            # ? ----------------------------------------------------------------

            connections_content = content.pop("connections")
            parsed_connections: list[Connection] = list()

            required_connection_keys = [
                "identifiers",
                "nodes",
                "scores",
            ]

            required_node_keys = [
                "accession",
                "marker",
                "metadata",
            ]

            if not isinstance(connections_content, list):
                return exc.InvalidArgumentError(
                    "Unable to load JSON. Connections must be a list.",
                    logger=LOGGER,
                )()

            for connection in connections_content:
                for grouped_key in required_connection_keys:
                    if grouped_key not in connection:
                        return exc.InvalidArgumentError(
                            f"Unable to load JSON. Missing key: `{grouped_key}`",
                            logger=LOGGER,
                        )()

                id = connection.pop("id")
                identifiers = connection.pop("identifiers")
                nodes = connection.pop("nodes")

                if not isinstance(identifiers, list):
                    return exc.InvalidArgumentError(
                        "Unable to load JSON. Identifiers must be a list.",
                        logger=LOGGER,
                    )()

                if not isinstance(nodes, list):
                    return exc.InvalidArgumentError(
                        "Unable to load JSON. Nodes must be a list.",
                        logger=LOGGER,
                    )()

                parsed_identifiers: list[str] = list()

                for identifier in identifiers:
                    if not isinstance(identifier, str):
                        return exc.InvalidArgumentError(
                            "Unable to load JSON. Identifier must be a string.",
                            logger=LOGGER,
                        )()

                    parsed_identifiers.append(identifier)

                parsed_nodes: list[Node] = list()

                for node in nodes:
                    for grouped_key in required_node_keys:
                        if grouped_key not in node:
                            return exc.InvalidArgumentError(
                                f"Unable to load JSON. Missing key: `{grouped_key}`",
                                logger=LOGGER,
                            )()

                    accession = node.pop("accession")
                    marker = node.pop("marker")
                    metadata = node.pop("metadata")

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

                        expected_metadata_key = MetadataKey(
                            group=group_enum,
                            key=key,
                        )

                        metadata_instance.add_feature(key=key, value=value)

                        if (
                            expected_metadata_key
                            not in metadata_instance.qualifiers
                        ):
                            return exc.InvalidArgumentError(
                                f"Unable to load JSON. Invalid metadata key: `{key}`.",
                                logger=LOGGER,
                            )()

                    parsed_nodes.append(
                        Node(
                            accession=accession,
                            marker=marker,
                            metadata=metadata_instance,
                        )
                    )

                scores: ConnectionScores | None = None
                if (parsed_scores := connection.get("scores")) is not None:
                    if not isinstance(parsed_scores, dict):
                        return exc.InvalidArgumentError(
                            "Unable to load JSON. Scores must be a dictionary.",
                            logger=LOGGER,
                        )()

                    for key, value in parsed_scores.items():
                        if not isinstance(key, str):
                            return exc.InvalidArgumentError(
                                "Unable to load JSON. Score key must be a string.",
                                logger=LOGGER,
                            )()

                        if not isinstance(value, (int, float)):
                            return exc.InvalidArgumentError(
                                "Unable to load JSON. Score value must be a number.",
                                logger=LOGGER,
                            )()

                    observed_completeness_score = parsed_scores.get(
                        "observed_completeness_score"
                    )

                    reachable_completeness_score = parsed_scores.get(
                        "reachable_completeness_score"
                    )

                    scores = ConnectionScores(
                        observed_completeness_score=observed_completeness_score,
                        reachable_completeness_score=reachable_completeness_score,
                    )

                connection = Connection(
                    identifiers=parsed_identifiers,
                    nodes=parsed_nodes,
                ).with_id(id)

                if scores is not None:
                    connection.with_scores(scores=scores)

                parsed_connections.append(connection)

            # ? ----------------------------------------------------------------
            # ? Load optional fields
            # ? ----------------------------------------------------------------

            optional_fields_content = content.pop("optional_fields")

            if not isinstance(optional_fields_content, list):
                return exc.InvalidArgumentError(
                    "Unable to load JSON. Optional fields must be a list.",
                    logger=LOGGER,
                )()

            # ? ----------------------------------------------------------------
            # ? Load gene fields
            # ? ----------------------------------------------------------------

            gene_fields_content = content.pop("gene_fields")

            if not isinstance(gene_fields_content, list):
                return exc.InvalidArgumentError(
                    "Unable to load JSON. Gene fields must be a list.",
                    logger=LOGGER,
                )()

            # ? ----------------------------------------------------------------
            # ? Load source data
            # ? ----------------------------------------------------------------

            data_content = content.pop("data")

            if not isinstance(data_content, list):
                return exc.InvalidArgumentError(
                    "Unable to load JSON. Data must be a list.",
                    logger=LOGGER,
                )()

            data_as_df = DataFrame.from_records(data_content)

            try:
                # Validate required data schema
                StandardFieldsSchema.validate(data_as_df)

                # Validate optional data schema
                OptionalColumnsSchema.validate(data_as_df)

                # Validate gene data schema
                cls.build_genes_schema_from_list(
                    genes=gene_fields_content,
                ).validate(data_as_df)

            except SchemaError as e:
                return exc.ExecutionError(
                    f"Invalid JSON content for data: {e}",
                    logger=LOGGER,
                )()

            # ? ----------------------------------------------------------------
            # ? Return a positive response
            # ? ----------------------------------------------------------------

            reference_data = cls(
                optional_fields=optional_fields_content,
                gene_fields=gene_fields_content,
                data=data_as_df,
            )

            reference_data.with_connections(connections=parsed_connections)

            return right(reference_data)

        except Exception as e:
            return exc.UseCaseError(e, logger=LOGGER)()
