from pathlib import Path

import click

from gcon.core.use_cases.run_gcon_pipeline import run_gcon_pipeline
from gcon.settings import LOGGER


# ? ----------------------------------------------------------------------------
# ? Initialize the CLI groups
# ? ----------------------------------------------------------------------------


@click.group()
def gcon_cmd() -> None:
    pass


@gcon_cmd.command(
    "resolve",
    help="Resolve a reference table",
)
@click.option(
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
@click.option(
    "-t",
    "--temporary-directory",
    required=True,
    prompt=True,
    type=click.Path(
        readable=True,
        exists=False,
        dir_okay=True,
        path_type=Path,
    ),
    help="A directory path to store temporary files",
)
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
    help="The system path of the output file",
)
@click.option(
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
def resolve_cmd(
    input_table: Path,
    temporary_directory: Path,
    output_file: Path,
    ignore_duplicates: bool,
) -> None:
    try:
        if not temporary_directory.is_dir():
            temporary_directory.mkdir(parents=True)

        response_either = run_gcon_pipeline(
            source_table_path=input_table,
            output_dir_path=temporary_directory,
            output_file=output_file,
            ignore_duplicates=ignore_duplicates,
        )

        if response_either.is_left:
            raise Exception(response_either.value.msg)

    except Exception as e:
        LOGGER.exception(e)