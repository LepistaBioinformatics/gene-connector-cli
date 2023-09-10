import gcon.core.domain.utils.exceptions as exc
from gcon.core.domain.dtos.metadata import Metadata
from gcon.core.domain.utils.either import Either, right
from gcon.settings import LOGGER


def place_qualifiers(
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
        if len(value) == 0:
            return exc.UseCaseError(
                f"Invalid qualifier value length for `{key}`. It should have"
                + f"at last one value. Found: {value}",
                logger=LOGGER,
            )()

        metadata.add_feature(key, value)

    return right(metadata)
