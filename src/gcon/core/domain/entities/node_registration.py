from typing import Any

from clean_base.either import Either
from clean_base.entities import (
    CreateManyResponse,
    CreateResponse,
    GetOrCreateResponse,
    Registration,
)
from clean_base.exceptions import CreationError

from gcon.core.domain.dtos.node import Node


class NodeRegistration(Registration):
    """A NodeRegistration entity."""

    # ? ------------------------------------------------------------------------
    # ? LIFE CYCLE HOOK METHODS
    # ? ------------------------------------------------------------------------

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

    # ? ------------------------------------------------------------------------
    # ? ABSTRACT METHODS DEFINITIONS
    # ? ------------------------------------------------------------------------

    def create(
        self,
        **kwargs: Any,  # type: ignore
    ) -> Either[CreationError, CreateResponse[Node]]:
        raise NotImplementedError

    def create_many(
        self,
        **kwargs: Any,  # type: ignore
    ) -> Either[CreationError, CreateManyResponse[Node]]:
        raise NotImplementedError

    def get_or_create(
        self,
        **kwargs: Any,  # type: ignore
    ) -> Either[CreationError, GetOrCreateResponse[Node]]:
        raise NotImplementedError
