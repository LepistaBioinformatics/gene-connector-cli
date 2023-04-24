from json import dumps
from pathlib import Path
from typing import Literal

import gcon.core.domain.utils.exceptions as exc
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
    ignore_duplicates: bool = False,
) -> Either[exc.UseCaseError, Literal[True]]:
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

        LOGGER.info(f"Loading source table: {source_table_path}")

        loading_response_either = load_and_validate_source_table(
            source_table_path=source_table_path,
            ignore_duplicates=ignore_duplicates,
        )

        if loading_response_either.is_left:
            return loading_response_either

        LOGGER.info("\tLoading done")

        # ? --------------------------------------------------------------------
        # ? Collect metadata
        # ? --------------------------------------------------------------------

        LOGGER.info("Collecting metadata")

        metadata_collection_response_either = collect_metadata(
            reference_data=loading_response_either.value,
            output_dir_path=output_dir_path,
        )

        if metadata_collection_response_either.is_left:
            return metadata_collection_response_either

        LOGGER.info("\tCollection done")

        # ? --------------------------------------------------------------------
        # ? Calculate metadata match scores
        # ? --------------------------------------------------------------------

        LOGGER.info("Calculating metadata match scores")

        calculation_response_either = build_metadata_match_scores(
            reference_data=metadata_collection_response_either.value,
        )

        if calculation_response_either.is_left:
            return calculation_response_either

        LOGGER.info("\tCalculation done")

        # ? --------------------------------------------------------------------
        # ? Persist results to temporary directory
        # ? --------------------------------------------------------------------

        LOGGER.info(f"Persisting results to file: {output_file}")

        with output_file.open("w") as f:
            f.write(
                dumps(
                    calculation_response_either.value.to_dict(),
                    indent=4,
                    sort_keys=True,
                )
            )

        # ? --------------------------------------------------------------------
        # ? Return success
        # ? --------------------------------------------------------------------

        return right(True)

    except Exception as e:
        return exc.UseCaseError(e, logger=LOGGER)()
