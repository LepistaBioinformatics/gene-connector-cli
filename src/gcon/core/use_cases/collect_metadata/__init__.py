from io import StringIO
from json import dump
from pathlib import Path
from typing import Generator

from Bio import Entrez, SeqIO
from Bio.SeqRecord import SeqRecord
from gcon.core.domain.dtos.connection import Connection
from gcon.core.domain.dtos.metadata import (
    Metadata,
    MetadataKeyGroup,
)
from gcon.core.domain.dtos.node import Node

import gcon.core.domain.utils.exceptions as exc
from gcon.core.domain.dtos.reference_data import ReferenceData
from gcon.core.domain.utils.either import Either, right
from gcon.settings import CHUNK_SIZE, CURRENT_USER_EMAIL, LOGGER


def collect_metadata(
    reference_data: ReferenceData,
    output_dir_path: Path,
) -> Either[exc.UseCaseError, ReferenceData]:
    # ? ------------------------------------------------------------------------
    # ? Validate input arguments
    # ? ------------------------------------------------------------------------

    if not isinstance(reference_data, ReferenceData):
        raise ValueError(
            f"`{reference_data}` is not a instance of `{ReferenceData}`"
        )

    if output_dir_path.is_dir() is False:
        raise ValueError(f"Invalid directory path: `{output_dir_path}`")

    # ? ------------------------------------------------------------------------
    # ? Collect accessions from marker columns values
    # ? ------------------------------------------------------------------------

    Entrez.email = CURRENT_USER_EMAIL

    by_marker_nodes: dict[str, list[Node]] = dict()

    LOGGER.info(f"Fetching sequence from user `{CURRENT_USER_EMAIL}`")

    for marker in reference_data.gene_fields:
        LOGGER.info(f"Recovering sequences from `{marker}` marker")

        marker_column = reference_data.data[marker]

        marker_nodes = __collect_single_gene_metadata(
            entrez_handle=Entrez,
            accessions=marker_column.dropna().values,
        )

        if marker_nodes.is_left:
            return marker_nodes

        by_marker_nodes.update({marker: marker_nodes.value})

        LOGGER.info(f"\t`{marker}`: {len(marker_nodes.value)} sequences found")

    LOGGER.info("Fetching sequence done")

    # ? ------------------------------------------------------------------------
    # ? Build output Connections
    # ? ------------------------------------------------------------------------

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
                acc_metadata = next(
                    i for i in gene_nodes if i.accession == gene_value
                )
            except StopIteration:
                return exc.UseCaseError(
                    f"Unable to find metadata for gene `{gene}`",
                    logger=LOGGER,
                )

            row_nodes.append(acc_metadata)

        identifiers = __collect_unique_identifiers(nodes=row_nodes)

        if identifiers.is_left:
            return identifiers

        connections.append(
            Connection(
                identifiers=identifiers.value,
                nodes=row_nodes,
            )
        )

    reference_data.with_connections(connections)

    # ? ------------------------------------------------------------------------
    # ? Persist connections to file
    # ? ------------------------------------------------------------------------

    marker_output_file = output_dir_path.joinpath("connections.json")

    LOGGER.info(f"Persisting metadata to file: {marker_output_file}")

    with marker_output_file.open("w") as marker_out:
        dump(
            reference_data.to_dict(),
            marker_out,
            indent=4,
        )

    LOGGER.info("\tDone")

    # ? ------------------------------------------------------------------------
    # ? Return a positive response
    # ? ------------------------------------------------------------------------

    return right(reference_data)


def __collect_unique_identifiers(
    nodes: list[Node],
) -> Either[exc.UseCaseError, set[str]]:
    identifiers: list[str] = list()

    for node in nodes:
        specimen_keys = [
            qualifier
            for qualifier in node.metadata.qualifiers.keys()
            if qualifier.group == MetadataKeyGroup.SPECIMEN
        ]

        if len(specimen_keys) == 0:
            return exc.UseCaseError(
                f"Unable to find specimen keys for node `{node}`",
                logger=LOGGER,
            )

        for qualifier in specimen_keys:
            identifiers.append(node.metadata.qualifiers.get(qualifier))

    return right(set(identifiers))


def __collect_single_gene_metadata(
    entrez_handle: Entrez,
    accessions: list[str],
) -> Either[exc.UseCaseError, list[Metadata]]:
    """Collect metadata from a list of accessions.

    Args:
        entrez_handle (Entrez): Entrez handle.
        accessions (list[str]): List of accessions.

    Returns:
        Either[exc.UseCaseError, list[Metadata]]: Either a UseCaseError or a
            list of Metadata.

    Raises:
        exc.UseCaseError: If the metadata source is not available.

    """

    nodes: list[Node] = []
    chunks = [i for i in __chunks(accessions, CHUNK_SIZE)]

    for index, acc_chunk in enumerate(chunks):
        LOGGER.info(
            f"Processing chunk {index + 1} of {len(chunks)}. "
            + f"Size: {len(acc_chunk)}"
        )

        parsed_content: list[SeqRecord] = []
        with entrez_handle.efetch(
            db="nuccore",
            id=",".join(acc_chunk),
            rettype="gb",
        ) as chunk_handle:
            parsed_content.extend(
                [
                    i
                    for i in SeqIO.parse(
                        StringIO(chunk_handle.read()), "genbank"
                    )
                ]
            )

        record: SeqRecord
        for record in parsed_content:
            try:
                source_feature = next(
                    feature
                    for feature in record.features
                    if feature.type == "source"
                )

            except StopIteration:
                return exc.UseCaseError(
                    f"Metadata source not available for `{record.id}`",
                    logger=LOGGER,
                )()

            record_metadata = __place_qualifiers(
                raw_qualifiers=source_feature.qualifiers,
            )

            if record_metadata.is_left:
                return record_metadata

            nodes.append(
                Node(
                    accession=record.name,
                    metadata=record_metadata.value,
                )
            )

    return right(nodes)


def __place_qualifiers(
    raw_qualifiers: dict[str, list[str | int]],
) -> Either[exc.UseCaseError, Metadata]:
    """Place qualifiers in the correct Metadata fields.

    Args:
        raw_qualifiers (dict[str, list[str | int]]): Raw qualifiers.

    Returns:
        Either[exc.UseCaseError, Metadata]: Either a UseCaseError or a Metadata.

    Raises:
        exc.UseCaseError: If the qualifier value length is not 1.
    """

    metadata = Metadata()

    for key, value in raw_qualifiers.items():
        if len(value) != 1:
            return exc.UseCaseError(
                f"Invalid qualifier value length for `{key}`. It should not"
                + f" have more than one value. Found: {value}",
                logger=LOGGER,
            )()

        metadata.add_feature(key, value[0])

    return right(metadata)


def __chunks(
    accessions: list[str],
    size: int,
) -> Generator[list[str], None, None]:
    """Yield successive n-sized chunks from l.

    Args:
        accessions (list[str]): List of accessions.
        size (int): Chunk size.

    Yields:
        Generator[list[str], None, None]: Generator of chunks.

    """

    for i in range(0, len(accessions), size):
        yield accessions[i : i + size]
