from typing import Any

from gcon.adapters.pickledb.repositories.connector import PickleDbConnector
from gcon.core.domain.dtos.node import Node
from gcon.core.domain.entities.node_fetching import NodeFetching
from gcon.core.domain.utils.either import Either, right
from gcon.core.domain.utils.entities import FetchManyResponse, FetchResponse
from gcon.core.domain.utils.exceptions import FetchingError
from gcon.settings import LOGGER


class NodeFetchingPickleDbRepository(NodeFetching):
    # ? ------------------------------------------------------------------------
    # ? CLASS ATTRIBUTES
    # ? ------------------------------------------------------------------------

    __conn: PickleDbConnector

    # ? ------------------------------------------------------------------------
    # ? LIFE CYCLE HOOK METHODS
    # ? ------------------------------------------------------------------------

    def __init__(self, db: PickleDbConnector | None) -> None:
        # This implementation is needed to alow users to pass a mock
        # TinyDbConnector on run tests.
        if db is not None:
            self.__conn = db

        # This implementation is needed to guarantee that the TinyDbConnector
        # instance will be initialized.
        if self.__conn is None:
            self.__conn = PickleDbConnector()

    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()

    # ? ------------------------------------------------------------------------
    # ? ABSTRACT CLASS METHODS IMPLEMENTATIONS
    # ? ------------------------------------------------------------------------

    def get(
        self,
        **kwargs: Any,
    ) -> Either[FetchingError, FetchResponse[Node]]:
        try:
            if (accession := kwargs.get("accession")) is None:
                return FetchingError(
                    "`accession` is required.",
                    logger=LOGGER,
                )()

            response = self.__conn.db.get(accession)
            self.__conn.db.dump()

            if not response or response is False:
                return right(FetchResponse(False, None))

            node_either: Either = Node.from_dict(response)

            if node_either.is_left:
                return node_either

            return right(FetchResponse(True, node_either.value))

        except Exception as e:
            raise FetchingError(e, logger=LOGGER)()

    # ? ------------------------------------------------------------------------
    # ! NOT IMPLEMENTED ABSTRACT METHODS
    # ? ------------------------------------------------------------------------

    def show(
        self,
        **kwargs: Any,
    ) -> Either[FetchingError, FetchManyResponse[Node]]:
        return super().show(**kwargs)
