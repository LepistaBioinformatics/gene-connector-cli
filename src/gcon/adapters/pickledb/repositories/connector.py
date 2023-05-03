from pathlib import Path
from typing import Self

from pickledb import PickleDB, load


class PickleDbConnector:
    # ? ------------------------------------------------------------------------
    # ? CLASS ATTRIBUTES
    # ? ------------------------------------------------------------------------

    __instance: Self | None = None
    __db: PickleDB | None = None

    # ? ------------------------------------------------------------------------
    # ? LIFE CYCLE HOOK METHODS
    # ? ------------------------------------------------------------------------

    def __new__(cls, db_path: Path) -> Self:
        if cls.__instance is None:
            if cls.__db is None:
                cls.__db = load(db_path, auto_dump=True)
            cls.__instance = super(PickleDbConnector, cls).__new__(cls)

        return cls.__instance  # type: ignore

    # ? ------------------------------------------------------------------------
    # ? PUBLIC METHODS
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
