from functools import reduce
from json import dump
from operator import iconcat
from pathlib import Path

from Bio import Entrez

import gcon.core.domain.utils.exceptions as exc
from gcon.core.domain.dtos.connection import Connection
from gcon.core.domain.dtos.node import Node
from gcon.core.domain.dtos.reference_data import ReferenceData
from gcon.core.domain.dtos.reference_data.schemas import StandardFieldsSchema
from gcon.core.domain.entities.node_fetching import NodeFetching
from gcon.core.domain.entities.node_registration import NodeRegistration
from gcon.core.domain.utils.either import Either, right
from gcon.core.domain.utils.lock import has_lock, lock
from gcon.core.domain.utils.slugify import slugify_string
from gcon.settings import CURRENT_USER_EMAIL, LOGGER

from ._collect_single_gene_metadata import collect_single_gene_metadata
from ._collect_unique_identifiers import collect_unique_identifiers


def collect_metadata(
    reference_data: ReferenceData,
    output_dir_path: Path,
    local_node_fetching_repo: NodeFetching,
    local_node_registration_repo: NodeRegistration,
) -> Either[exc.MappedErrors, ReferenceData]:
    """Collect metadata from a list of accessions.

    Args:
        reference_data (ReferenceData): Reference data.
        output_dir_path (Path): Output directory path.
        local_node_fetching_repo (NodeFetching): Local node fetching repository.
        local_node_registration_repo (NodeRegistration): Local node registration
            repository.

    Returns:
        Either[exc.UseCaseError, ReferenceData]: Either a UseCaseError or a
            ReferenceData.

    Raises:
        exc.UseCaseError: If the metadata source is not available or if the
            output directory path is not valid.

    """

    try:
        # ? --------------------------------------------------------------------
        # ? Validate input arguments
        # ? --------------------------------------------------------------------

        if not isinstance(reference_data, ReferenceData):
            return exc.InvalidArgumentError(
                f"`{reference_data}` is not a instance of `{ReferenceData}`",
                logger=LOGGER,
            )

        if output_dir_path.is_dir() is False:
            return exc.InvalidArgumentError(
                f"Invalid directory path: `{output_dir_path}`",
                logger=LOGGER,
            )

        # ? --------------------------------------------------------------------
        # ? Collect accessions from marker columns values
        # ? --------------------------------------------------------------------

        marker_output_file = output_dir_path.joinpath("reference_data.json")

        lock_config = dict(
            base_dir=output_dir_path,
            step=slugify_string(collect_metadata.__name__),
        )

        if has_lock(**lock_config):
            if (
                reference_data_either := ReferenceData.from_json(
                    json_path=marker_output_file,
                )
            ).is_left:
                return reference_data_either

            return right(reference_data_either.value)

        # ? --------------------------------------------------------------------
        # ? Collect accessions from marker columns values
        # ? --------------------------------------------------------------------

        if CURRENT_USER_EMAIL is None:
            return exc.UseCaseError(
                "`CURRENT_USER_EMAIL` not configured correctly. Please "
                "configure before running the pipeline.",
                logger=LOGGER,
            )()

        Entrez.email = CURRENT_USER_EMAIL

        by_marker_nodes: dict[str, list[Node]] = dict()

        LOGGER.debug(f"Fetching sequence from user `{CURRENT_USER_EMAIL}`")
        LOGGER.debug("")

        for marker in reference_data.gene_fields:
            LOGGER.debug(f"Recovering sequences from `{marker}` marker")

            marker_nodes = collect_single_gene_metadata(
                entrez_handle=Entrez,
                marker=marker,
                accessions=reduce(
                    iconcat,
                    reference_data.data[marker].dropna().values,
                    [],
                ),
                local_node_fetching_repo=local_node_fetching_repo,
                local_node_registration_repo=local_node_registration_repo,
            )

            if marker_nodes.is_left:
                return marker_nodes

            by_marker_nodes.update({marker: marker_nodes.value})

            LOGGER.debug(
                f"`{marker}`: {len(marker_nodes.value)} sequences found"
            )

            LOGGER.debug("")

        LOGGER.info("Fetching sequence done")

        # ? --------------------------------------------------------------------
        # ? Build output Connections
        # ? --------------------------------------------------------------------

        connections: list[Connection] = list()
        for _, row in reference_data.data.iterrows():
            row_nodes: list[Node] = list()

            for gene in reference_data.gene_fields:
                if (gene_value := row.get(gene)) is None:
                    continue

                if (gene_nodes := by_marker_nodes.get(gene)) is None:
                    return exc.UseCaseError(
                        f"Unable to find metadata for gene `{gene}`",
                        logger=LOGGER,
                    )

                try:
                    acc_metadata = [
                        i for i in gene_nodes if i.accession in gene_value
                    ]
                except StopIteration:
                    continue

                row_nodes.extend(acc_metadata)

            identifiers = collect_unique_identifiers(
                nodes=row_nodes,
            )

            if identifiers.is_left:
                return identifiers

            if (
                row_identifier := row.get(StandardFieldsSchema.identifier)
            ) is None:
                return exc.UseCaseError(
                    f"Unable to find identifier for row `{row}`",
                    logger=LOGGER,
                )()

            unique_identifiers = set(
                [
                    *list(identifiers.value),
                    row_identifier,
                ]
            )

            connections.append(
                Connection(
                    identifiers=unique_identifiers,
                    nodes=row_nodes,
                ).with_id(row.get("uuid"))
            )

        reference_data.with_connections(connections)

        # ? --------------------------------------------------------------------
        # ? Persist connections to file
        # ? --------------------------------------------------------------------

        LOGGER.debug(
            f"Persisting metadata to temporary file: {marker_output_file}"
        )

        with marker_output_file.open("w") as marker_out:
            dump(
                reference_data.to_dict(),
                marker_out,
                indent=4,
                sort_keys=True,
                default=str,
            )

        # ? --------------------------------------------------------------------
        # ? Lock the step execution
        # ? --------------------------------------------------------------------

        lock(**lock_config)

        # ? --------------------------------------------------------------------
        # ? Return a positive response
        # ? --------------------------------------------------------------------

        return right(reference_data)

    except Exception as e:
        return exc.UseCaseError(e, logger=LOGGER)()
