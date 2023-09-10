from typing import Generator


def chunks_accessions(
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
