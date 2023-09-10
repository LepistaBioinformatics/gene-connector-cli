from logging import WARNING, Formatter, StreamHandler, getLogger
from os import getenv
from sys import stdout

from clean_base.settings import LOGGING_LEVEL

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
#
# ! IMPORTANT
# ! This is needed to avoid the following warning message:
# ! "UserWarning: BibTeX Mako templates not found in the current directory"
#
getLogger("bibtexparser").setLevel(WARNING)


# ? ----------------------------------------------------------------------------
# ? Get user credentials from environment
# ? ----------------------------------------------------------------------------


CURRENT_USER_EMAIL: str | None = getenv("CURRENT_USER_EMAIL")


# ? ----------------------------------------------------------------------------
# ? Accessions chunk default size configuration
# ? ----------------------------------------------------------------------------


CHUNK_SIZE = int(getenv("CHUNK_SIZE", 15))
