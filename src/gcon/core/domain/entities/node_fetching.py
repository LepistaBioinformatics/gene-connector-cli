from typing import Any
from gcon.core.domain.utils.either import Either
from gcon.core.domain.utils.entities import (
    Fetching,
    FetchManyResponse,
    FetchResponse,
)
from gcon.core.domain.dtos.node import Node
from gcon.core.domain.utils.exceptions import FetchingError


class NodeFetching(Fetching):
    """A StandardFetching entity."""

    # ? ------------------------------------------------------------------------
    # ? LIFE CYCLE HOOK METHODS
    # ? ------------------------------------------------------------------------

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

    # ? ------------------------------------------------------------------------
    # ? ABSTRACT METHODS DEFINITIONS
    # ? ------------------------------------------------------------------------

    def show(
        self,
        **kwargs: Any,
    ) -> Either[FetchingError, FetchManyResponse[Node]]:
        raise NotImplementedError

    def get(
        self,
        **kwargs: Any,
    ) -> Either[FetchingError, FetchResponse[Node]]:
        raise NotImplementedError
