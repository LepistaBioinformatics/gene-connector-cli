from pathlib import Path

import click

from gcon.__version__ import version
from gcon.adapters.pickledb.repositories.connector import PickleDbConnector
from gcon.adapters.pickledb.repositories.node_fetching import (
    NodeFetchingPickleDbRepository,
)
from gcon.adapters.pickledb.repositories.node_registration import (
    NodeRegistrationPickleDbRepository,
)
from gcon.core.use_cases import (
    load_and_validate_source_table,
    run_gcon_pipeline,
)
from gcon.settings import LOGGER
from gcon.core.use_cases.load_and_validate_source_table._dtos import (
    SourceGenomeEnum,
)

# ? ----------------------------------------------------------------------------
# ? Initialize CLI groups
# ? ----------------------------------------------------------------------------


@click.group()
@click.version_option(version)
def gcon_cmd() -> None:
    pass


@gcon_cmd.group(
    "info",
    help="Get information and examples about the Gcon utility",
)
def info_cmd() -> None:
    pass


# ? ----------------------------------------------------------------------------
# ? Create CLI shared options
# ? ----------------------------------------------------------------------------


__INPUT_TABLE = click.option(
    "-i",
    "--input-table",
    required=True,
    prompt=True,
    type=click.Path(
        resolve_path=True,
        readable=True,
        exists=True,
        file_okay=True,
        path_type=Path,
    ),
    help="A reference table to resolve",
)


__IGNORE_DUPLICATES = click.option(
    "-i",
    "--ignore-duplicates",
    is_flag=True,
    show_default=True,
    default=False,
    help=(
        "Ignore duplicate gene accession numbers in the source table if True. "
        + "This is usual in cases which the same code is used for continuous "
        + "genes. This is a common situation at ribosomal genes."
    ),
)


# ? ----------------------------------------------------------------------------
# ? Create CLI commands
# ? ----------------------------------------------------------------------------


@info_cmd.command(
    "source-genomes",
    help="Get information about the allowed source genomes",
)
def source_genomes_cmd() -> None:
    for option, example in [
        (
            SourceGenomeEnum.NUCLEUS,
            f"{SourceGenomeEnum.NUCLEUS.value}-its",
        ),
        (
            SourceGenomeEnum.MITOCHONDRIA,
            f"{SourceGenomeEnum.MITOCHONDRIA.value}-gapdh",
        ),
        (
            SourceGenomeEnum.PLASTID,
            f"{SourceGenomeEnum.PLASTID.value}-rbcl",
        ),
        (
            SourceGenomeEnum.UNKNOWN,
            f"{SourceGenomeEnum.UNKNOWN.value}-gene",
        ),
    ]:
        click.echo("-" * 40)
        click.echo(f"Source genome: {option.name} ({option.value})")
        click.echo(f"  Example: {example}")
        click.echo()


@gcon_cmd.command(
    "validate",
    help="Validate a reference table",
)
@__INPUT_TABLE
@__IGNORE_DUPLICATES
def validate_cmd(
    input_table: Path,
    ignore_duplicates: bool,
) -> None:
    if (
        left_response := load_and_validate_source_table(
            source_table_path=input_table,
            ignore_duplicates=ignore_duplicates,
        )
    ).is_left:
        raise Exception(left_response.value)


@gcon_cmd.command(
    "resolve",
    help="Resolve a reference table.",
)
@__INPUT_TABLE
@click.option(
    "-o",
    "--output-file",
    required=True,
    prompt=True,
    type=click.Path(
        resolve_path=True,
        exists=False,
        file_okay=True,
        path_type=Path,
    ),
    help="The system path of the output file. Please ignore file extension.",
)
@__IGNORE_DUPLICATES
@click.option(
    "-t",
    "--temporary-directory",
    required=False,
    default=Path("tmp"),
    type=click.Path(
        readable=True,
        exists=False,
        dir_okay=True,
        path_type=Path,
    ),
    help="A directory path to store temporary files.",
)
@click.option(
    "--cache-file",
    required=False,
    default=Path("cache.json"),
    type=click.Path(
        resolve_path=True,
        readable=True,
        file_okay=True,
        path_type=Path,
    ),
    help=(
        "A path to the JSON cache file used to persist intermediary records "
        + "from the pipeline. This is useful to avoid reprocessing the same "
        + "data when the pipeline is interrupted."
    ),
)
def resolve_cmd(
    input_table: Path,
    temporary_directory: Path,
    output_file: Path,
    ignore_duplicates: bool,
    cache_file: Path,
) -> None:
    if not temporary_directory.is_dir():
        temporary_directory.mkdir(parents=True)

    try:
        connector = PickleDbConnector(
            db_path=Path(cache_file).with_suffix(".json")
        )
    except Exception as e:
        LOGGER.exception(e)
        raise Exception("Could not initialize PickleDbConnector.")

    if (
        response_either := run_gcon_pipeline(
            source_table_path=input_table,
            output_dir_path=temporary_directory,
            output_file=output_file,
            ignore_duplicates=ignore_duplicates,
            local_node_fetching_repo=NodeFetchingPickleDbRepository(
                db=connector,
            ),
            local_node_registration_repo=NodeRegistrationPickleDbRepository(
                db=connector,
            ),
        )
    ).is_left:
        raise Exception(response_either.value.msg)
