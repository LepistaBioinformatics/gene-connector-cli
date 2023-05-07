from typing import Any

from gcon.adapters.pickledb.repositories.connector import PickleDbConnector
from gcon.core.domain.dtos.node import Node
from gcon.core.domain.entities.node_registration import NodeRegistration
from gcon.core.domain.utils.either import Either, right
from gcon.core.domain.utils.entities import (
    CreateManyResponse,
    CreateResponse,
    GetOrCreateResponse,
)
from gcon.core.domain.utils.exceptions import CreationError
from gcon.settings import LOGGER


class NodeRegistrationPickleDbRepository(NodeRegistration):
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
            db = PickleDbConnector()

    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()

    # ? ------------------------------------------------------------------------
    # ? ABSTRACT CLASS METHODS IMPLEMENTATIONS
    # ? ------------------------------------------------------------------------

    def create_many(
        self,
        **kwargs: Any,  # type: ignore
    ) -> Either[CreationError, CreateManyResponse[Node]]:
        try:
            if (nodes := kwargs.get("nodes")) is None:
                return CreationError(
                    "Node is required.",
                    logger=LOGGER,
                )()

            if not isinstance(nodes, list):
                return CreationError(
                    "Node must be an list.",
                    logger=LOGGER,
                )()

            for node in nodes:
                if not isinstance(node, Node):
                    return CreationError(
                        "Node must be an instance of Node.",
                        logger=LOGGER,
                    )()

            for node in nodes:
                node_dict = node.to_dict()

                if not node_dict:
                    LOGGER.warning(
                        f"Node {node.accession} was not cached because it is empty."
                    )

                    continue

                self.__conn.db.set(node.accession, node.to_dict())

            self.__conn.db.dump()

            return right(CreateManyResponse(True, nodes))

        except Exception as e:
            return CreationError(e, logger=LOGGER)()

    # ? ------------------------------------------------------------------------
    # ! NOT IMPLEMENTED ABSTRACT METHODS
    # ? ------------------------------------------------------------------------

    def create(
        self,
        **kwargs: Any,
    ) -> Either[CreationError, CreateResponse[Node]]:
        return super().create(**kwargs)

    def get_or_create(
        self,
        **kwargs: Any,
    ) -> Either[CreationError, GetOrCreateResponse[Node]]:
        return super().get_or_create(**kwargs)
