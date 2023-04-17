from pathlib import Path

from gcon.settings import LOGGER
import gcon.core.domain.utils.exceptions as gcon_exc


def load_and_validate_source_table(
    source_table: Path,
) -> None:
    try:
        # ? --------------------------------------------------------------------
        # ? Validate entry params
        # ? --------------------------------------------------------------------

        if not source_table.exists():
            return gcon_exc.InvalidArgumentError(
                f"Source table file not found: {source_table}",
                logger=LOGGER,
            )()

        # ? --------------------------------------------------------------------
        # ? Load source table
        # ? --------------------------------------------------------------------

        ...

    except Exception as e:
        return gcon_exc.UseCaseError(e, logger=LOGGER)()
