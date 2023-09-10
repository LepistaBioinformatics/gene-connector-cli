from io import StringIO

import clean_base.exceptions as exc
from Bio import Entrez, SeqIO
from Bio.SeqRecord import SeqRecord
from clean_base.either import Either, right
from clean_base.entities import FetchResponse

from gcon.core.domain.dtos.metadata import Metadata
from gcon.core.domain.dtos.node import Node
from gcon.core.domain.entities.node_fetching import NodeFetching
from gcon.core.domain.entities.node_registration import NodeRegistration
from gcon.settings import CHUNK_SIZE, LOGGER

from ._chunks_accessions import chunks_accessions
from ._place_qualifiers import place_qualifiers


def collect_single_gene_metadata(
    entrez_handle: Entrez,
    accessions: list[str],
    marker: str,
    local_node_fetching_repo: NodeFetching,
    local_node_registration_repo: NodeRegistration,
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

    # ? ------------------------------------------------------------------------
    # ? Collect nodes from local storage
    #
    # Locally stored nodes includes nodes that were previously fetched from
    # Entrez and stored in the local storage. This is done to avoid fetching
    # the same nodes multiple times.
    #
    # ? ------------------------------------------------------------------------

    LOGGER.debug(f"Collecting nodes from local storage for `{marker}` marker")

    cached_accessions: list[Node] = []
    new_accessions: list[Node] = []

    for accession in accessions:
        local_nodes_response_either = local_node_fetching_repo.get(
            accession=accession,
        )

        if local_nodes_response_either.is_left:
            return local_nodes_response_either

        fetch_response: FetchResponse = local_nodes_response_either.value

        if fetch_response.fetched is False:
            new_accessions.append(accession)
            continue

        cached_accessions.append(fetch_response.instance)

    LOGGER.debug(
        f"Found {len(cached_accessions)} cached nodes for `{marker}` marker"
    )

    # ? ------------------------------------------------------------------------
    # ? Populate not already stored accessions
    #
    # Accessions that are not already stored in the local storage are fetched
    # from Entrez and stored in the local storage.
    #
    # ? ------------------------------------------------------------------------

    nodes: list[Node] = []
    chunks = [i for i in chunks_accessions(new_accessions, CHUNK_SIZE)]

    for index, acc_chunk in enumerate(chunks):
        LOGGER.debug(
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
        chunk_nodes: list[Node] = []
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

            record_metadata = place_qualifiers(
                raw_qualifiers=source_feature.qualifiers,
            )

            if record_metadata.is_left:
                return record_metadata

            chunk_nodes.append(
                Node(
                    accession=record.name,
                    marker=marker,
                    metadata=record_metadata.value,
                )
            )

        if (
            response_either := local_node_registration_repo.create_many(
                nodes=[*chunk_nodes, *cached_accessions]
            )
        ).is_left:
            return response_either

        nodes.extend(chunk_nodes)

    return right([*nodes, *cached_accessions])
