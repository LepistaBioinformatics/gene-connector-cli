from pathlib import Path
from typing import Self

from pickledb import PickleDB, load

from gcon.settings import LOGGER


class PickleDbConnector:
    # ? ------------------------------------------------------------------------
    # ? CLASS ATTRIBUTES
    # ? ------------------------------------------------------------------------

    __instance: Self | None = None
    __db_path: Path | None = None
    __db: PickleDB | None = None

    # ? ------------------------------------------------------------------------
    # ? LIFE CYCLE HOOK METHODS
    # ? ------------------------------------------------------------------------

    def __new__(cls, db_path: Path) -> Self:
        cls.__db_path = db_path

        if cls.__instance is None:
            if cls.__db is None:
                cls.load(cls)  # type: ignore

            LOGGER.info(
                "PickleDB database was initialized with size: "
                + f"{cls.__db.totalkeys()}"  # type: ignore
            )

            cls.__instance = super(PickleDbConnector, cls).__new__(cls)

        return cls.__instance  # type: ignore

    # ? ------------------------------------------------------------------------
    # ? PUBLIC PROPERTIES
    # ? ------------------------------------------------------------------------

    @property
    def db(self) -> PickleDB:
        """Returns the PickleDB instance.

        Raises:
            ValueError: If the TinyDB instance is not initialized.
        """

        if self.__db is None:
            raise ValueError("PickleDB instance is not initialized.")

        return self.__db

    # ? ------------------------------------------------------------------------
    # ? PUBLIC METHODS
    # ? ------------------------------------------------------------------------

    def load(self) -> None:
        """Loads the PickleDB instance."""

        self.__db = load(
            self.__db_path,
            auto_dump=False,
        )
