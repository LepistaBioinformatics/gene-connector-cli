from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    FATAL,
    INFO,
    NOTSET,
    WARN,
    WARNING,
    basicConfig,
    getLogger,
)
from os import getenv

# ? ----------------------------------------------------------------------------
# ? Build logger configurations
# ? ----------------------------------------------------------------------------


LOGGING_LEVEL = DEBUG


ENV_LOGGING_LEVEL = getenv("LOGGING_LEVEL")


if ENV_LOGGING_LEVEL is not None:
    ENV_LOGGING_LEVEL = eval(ENV_LOGGING_LEVEL.upper())

    if ENV_LOGGING_LEVEL not in [
        CRITICAL,
        DEBUG,
        ERROR,
        FATAL,
        INFO,
        NOTSET,
        WARN,
        WARNING,
    ]:
        raise ValueError(
            f"Invalid `ENV_LOGGING_LEVEL` value from env: {ENV_LOGGING_LEVEL}"
        )

    LOGGING_LEVEL = ENV_LOGGING_LEVEL  # type: ignore


# ? ----------------------------------------------------------------------------
# ? Initialize global logger
# ? ----------------------------------------------------------------------------


basicConfig(
    level=DEBUG,
    format="%(levelname)s\t[ %(asctime)s ]\t%(message)s",
)


LOGGER = getLogger("gcon")

getLogger("bibtexparser").setLevel(WARNING)

LOGGER.setLevel(LOGGING_LEVEL)


# ? ----------------------------------------------------------------------------
# ? Get user credentials from environment
# ? ----------------------------------------------------------------------------


CURRENT_USER_EMAIL: str | None = None


ENV_CURRENT_USER_EMAIL = getenv("CURRENT_USER_EMAIL")


if ENV_CURRENT_USER_EMAIL is None:
    raise EnvironmentError(
        "`CURRENT_USER_EMAIL` environment variable not configured"
    )


CURRENT_USER_EMAIL = ENV_CURRENT_USER_EMAIL


if CURRENT_USER_EMAIL is None:
    raise EnvironmentError(
        "`CURRENT_USER_EMAIL` not configured correctly. Please contact the "
        + "system developers"
    )


# ? ----------------------------------------------------------------------------
# ? Accessions chunk default size configuration
# ? ----------------------------------------------------------------------------


CHUNK_SIZE = 15
