from typing import Any

from clean_base.either import Either
from clean_base.entities import Fetching, FetchManyResponse, FetchResponse
from clean_base.exceptions import FetchingError

from gcon.core.domain.dtos.node import Node


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
