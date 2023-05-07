from json import dumps
from pathlib import Path
from typing import Any, Literal

from pandas import DataFrame
from gcon.core.domain.dtos.metadata import MetadataKey
from gcon.core.domain.dtos.reference_data import ReferenceData
from gcon.core.domain.dtos.reference_data.schemas import StandardFieldsSchema

import gcon.core.domain.utils.exceptions as exc
from gcon.core.domain.entities.node_fetching import NodeFetching
from gcon.core.domain.entities.node_registration import NodeRegistration
from gcon.core.domain.utils.either import Either, right
from gcon.core.use_cases.build_metadata_match_scores import (
    build_metadata_match_scores,
)
from gcon.core.use_cases.collect_metadata import collect_metadata
from gcon.core.use_cases.load_and_validate_source_table import (
    load_and_validate_source_table,
)
from gcon.settings import LOGGER


def run_gcon_pipeline(
    source_table_path: Path,
    output_dir_path: Path,
    output_file: Path,
    local_node_fetching_repo: NodeFetching,
    local_node_registration_repo: NodeRegistration,
    ignore_duplicates: bool = False,
) -> Either[exc.UseCaseError, Literal[True]]:
    def section_log(msg: str) -> None:
        LOGGER.info("")
        LOGGER.info("-" * 80)
        LOGGER.info(msg.upper())
        LOGGER.info("")

    try:
        # ? --------------------------------------------------------------------
        # ? Validate entry params
        # ? --------------------------------------------------------------------

        if not source_table_path.exists():
            return exc.InvalidArgumentError(
                f"Source table file not found: {source_table_path}",
                logger=LOGGER,
            )()

        # ? --------------------------------------------------------------------
        # ? Load source data
        # ? --------------------------------------------------------------------

        section_log("LOADING SOURCE METADATA")

        LOGGER.info(f"Try to load from {source_table_path}")

        loading_response_either = load_and_validate_source_table(
            source_table_path=source_table_path,
            ignore_duplicates=ignore_duplicates,
        )

        if loading_response_either.is_left:
            return loading_response_either

        # ? --------------------------------------------------------------------
        # ? Collect metadata
        # ? --------------------------------------------------------------------

        section_log("COLLECTING METADATA FROM GENBANK")

        metadata_collection_response_either = collect_metadata(
            reference_data=loading_response_either.value,
            output_dir_path=output_dir_path,
            local_node_fetching_repo=local_node_fetching_repo,
            local_node_registration_repo=local_node_registration_repo,
        )

        if metadata_collection_response_either.is_left:
            return metadata_collection_response_either

        # ? --------------------------------------------------------------------
        # ? Calculate metadata match scores
        # ? --------------------------------------------------------------------

        section_log("CALCULATING METADATA MATCH SCORES")

        calculation_response_either = build_metadata_match_scores(
            reference_data=metadata_collection_response_either.value,
        )

        if calculation_response_either.is_left:
            return calculation_response_either

        LOGGER.info("Metadata match scores calculated successfully")

        # ? --------------------------------------------------------------------
        # ? Persist results to temporary directory
        # ? --------------------------------------------------------------------

        section_log("PERSISTING RESULTS LOCALLY")

        LOGGER.info(f"Persisting JSON results to file: {output_file}.json")

        with output_file.with_suffix(".json").open("w") as f:
            f.write(
                dumps(
                    calculation_response_either.value.to_dict(),
                    indent=4,
                    sort_keys=True,
                    default=str,
                )
            )

        LOGGER.info(f"Persisting TSV results to file: {output_file}.tsv")

        __build_metadata_table(
            reference_data=metadata_collection_response_either.value,
            output_file=output_file.with_suffix(".tsv"),
        )

        LOGGER.info("")

        # ? --------------------------------------------------------------------
        # ? Return success
        # ? --------------------------------------------------------------------

        return right(True)

    except Exception as e:
        return exc.UseCaseError(e, logger=LOGGER)()


def __build_metadata_table(
    reference_data: ReferenceData,
    output_file: Path,
) -> Either[exc.UseCaseError, Literal[True]]:
    JOIN_SEPARATOR = " / "

    def build_metadata_string_key(key: MetadataKey) -> str:
        return f"{key.group.name}.{key.key}"

    try:
        # ? --------------------------------------------------------------------
        # ? Collect all unique keys
        # ? --------------------------------------------------------------------

        unique_marker_keys: set[str] = set()
        unique_metadata_keys: set[str] = set()

        for connection in reference_data.connections:
            for node in connection.nodes:
                unique_marker_keys.add(node.marker)

                unique_metadata_keys = unique_metadata_keys.union(
                    {
                        build_metadata_string_key(key=qualifier_key)
                        for qualifier_key in node.metadata.qualifiers.keys()
                    }
                )

        # ? --------------------------------------------------------------------
        # ? Build dataframe
        # ? --------------------------------------------------------------------

        data_source: list[dict[str, Any]] = []

        for connection in reference_data.connections:
            connection_record: dict[str, Any] = {}

            connection_record.update(
                {
                    "id": connection.id,
                    StandardFieldsSchema.identifier: f"{JOIN_SEPARATOR}".join(
                        set(connection.identifiers)
                    ),
                    "observed_completeness_score": connection.scores.observed_completeness_score,
                    "reachable_completeness_score": connection.scores.reachable_completeness_score,
                }
            )

            for node in connection.nodes:
                accession = node.accession
                if node.marker in connection_record:
                    accession = f"{JOIN_SEPARATOR}".join(
                        [accession, node.accession]
                    )
                connection_record.update({node.marker: accession})

                for key, value in node.metadata.qualifiers.items():
                    composed_key = build_metadata_string_key(key=key)
                    stringified_value = (
                        value
                        if isinstance(value, str)
                        else f"{JOIN_SEPARATOR}".join(value)
                    )

                    if composed_key in connection_record:
                        stringified_value = f"{JOIN_SEPARATOR}".join(
                            [
                                *connection_record[composed_key],
                                stringified_value,
                            ]
                        )

                    connection_record.update(
                        {
                            build_metadata_string_key(
                                key=key
                            ): stringified_value
                            if isinstance(value, str)
                            else ",".join(value)
                        }
                    )

            data_source.append(connection_record)

        output_df = DataFrame.from_records(data_source)

        output_df["information_gain"] = 100 - (
            output_df["observed_completeness_score"]
            * 100
            / output_df["reachable_completeness_score"]
        )

        output_df.merge(
            right=reference_data.data[
                [
                    c
                    for c in reference_data.data.columns
                    if c
                    in [
                        "uuid",
                        StandardFieldsSchema.sci_name,
                        *reference_data.optional_fields,
                    ]
                ]
            ],
            how="left",
            left_on="id",
            right_on="uuid",
        ).reindex(
            [
                "id",
                StandardFieldsSchema.identifier,
                StandardFieldsSchema.sci_name,
                *reference_data.optional_fields,
                "observed_completeness_score",
                "reachable_completeness_score",
                "information_gain",
                *sorted(unique_marker_keys),
                *sorted(unique_metadata_keys),
            ],
            axis=1,
        ).to_csv(
            path_or_buf=output_file.with_suffix(".tsv"),
            sep="\t",
            index=False,
        )

        # ? --------------------------------------------------------------------
        # ? Return success
        # ? --------------------------------------------------------------------

        return right(True)

    except Exception as e:
        return exc.UseCaseError(e, logger=LOGGER)()
