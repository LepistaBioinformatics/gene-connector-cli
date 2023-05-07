from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    FATAL,
    INFO,
    NOTSET,
    WARN,
    WARNING,
    Formatter,
    StreamHandler,
    getLogger,
)
from os import getenv
from sys import stdout

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


LOGGER = getLogger("gcon")


LOGGER.setLevel(LOGGING_LEVEL)


formatter = Formatter(
    "%(levelname)s\t[ %(asctime)s ]\t%(message)s",
    datefmt="%Y-%d-%m %H:%M:%S",
)


stdout_handler = StreamHandler(stdout)


stdout_handler.setFormatter(formatter)


LOGGER.addHandler(stdout_handler)


# ? Configure bibtexparser external library logger
getLogger("bibtexparser").setLevel(WARNING)


# ? ----------------------------------------------------------------------------
# ? Get user credentials from environment
# ? ----------------------------------------------------------------------------


CURRENT_USER_EMAIL: str | None = getenv("CURRENT_USER_EMAIL")


# ? ----------------------------------------------------------------------------
# ? Accessions chunk default size configuration
# ? ----------------------------------------------------------------------------


CHUNK_SIZE = 15


# ? ----------------------------------------------------------------------------
# ? The file to lock processed steps
# ? ----------------------------------------------------------------------------


LOCK_FILE = "finished-{step}.lock"
