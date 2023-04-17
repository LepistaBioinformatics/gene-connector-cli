from abc import ABCMeta, abstractmethod
from typing import Any, NamedTuple

from .either import Either
from .exceptions import (
    CreationError,
    DeletionError,
    ExecutionError,
    FetchingError,
    UpdatingError,
)

# ------------------------------------------------------------------------------
# DEFAULT RESPONSE TYPES
# ------------------------------------------------------------------------------


class CreateResponse(NamedTuple):
    """A interface for creation return methods."""

    created: bool
    instance: Any


class GetOrCreateResponse(NamedTuple):
    """A interface for get_or_creation return methods."""

    created: bool
    instance: Any


class FetchResponse(NamedTuple):
    """A interface for fetch return methods."""

    fetched: bool
    instance: Any | None


class FetchManyResponse(NamedTuple):
    """A interface for fetch return methods."""

    fetched: bool
    instance: list[Any] | None


class UpdateResponse(NamedTuple):
    """A interface for update return methods."""

    updated: bool
    instance: Any


class UpdateManyResponse(NamedTuple):
    """A interface for update return methods."""

    updated: bool
    records: int


class DeleteResponse(NamedTuple):
    """A interface for delete return methods."""

    deleted: bool
    instance: Any


class ExecuteResponse(NamedTuple):
    """A interface for execution return methods."""

    executed: bool
    instance: Any


class Fetching(metaclass=ABCMeta):
    """The registration interface."""

    # --------------------------------------------------------------------------
    # LIFE CYCLE HOOK METHODS
    # --------------------------------------------------------------------------

    def __init_subclass__(cls) -> None:
        pass

    # --------------------------------------------------------------------------
    # ABSTRACT METHODS
    # --------------------------------------------------------------------------

    @abstractmethod
    def show(
        self,
        term: str | None = None,
        page: int = 1,
        size: int = 10,
        **kwargs: Any,
    ) -> Either[FetchingError, FetchManyResponse]:
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        pk: int | None = None,
        other: str | None = None,
        **kwargs: Any,
    ) -> Either[FetchingError, FetchResponse]:
        raise NotImplementedError


class Registration(metaclass=ABCMeta):
    """The registration interface."""

    # --------------------------------------------------------------------------
    # LIFE CYCLE HOOK METHODS
    # --------------------------------------------------------------------------

    def __init_subclass__(cls) -> None:
        pass

    # --------------------------------------------------------------------------
    # ABSTRACT METHODS
    # --------------------------------------------------------------------------

    @abstractmethod
    def create(
        self,
        **kwargs: Any,
    ) -> Either[CreationError, CreateResponse]:
        raise NotImplementedError

    @abstractmethod
    def get_or_create(
        self,
        **kwargs: Any,
    ) -> Either[CreationError, GetOrCreateResponse]:
        raise NotImplementedError


class Updating(metaclass=ABCMeta):
    """The updating interface."""

    # --------------------------------------------------------------------------
    # LIFE CYCLE HOOK METHODS
    # --------------------------------------------------------------------------

    def __init_subclass__(cls) -> None:
        pass

    # --------------------------------------------------------------------------
    # ABSTRACT METHODS
    # --------------------------------------------------------------------------

    @abstractmethod
    def update(
        self,
        **kwargs: Any,
    ) -> Either[UpdatingError, UpdateResponse]:
        raise NotImplementedError


class Deletion(metaclass=ABCMeta):
    """The deletion interface."""

    # --------------------------------------------------------------------------
    # LIFE CYCLE HOOK METHODS
    # --------------------------------------------------------------------------

    def __init_subclass__(cls) -> None:
        pass

    # --------------------------------------------------------------------------
    # ABSTRACT METHODS
    # --------------------------------------------------------------------------

    @abstractmethod
    def delete(
        self,
        **kwargs: Any,
    ) -> Either[DeletionError, DeleteResponse]:
        raise NotImplementedError


class ExecuteStep(metaclass=ABCMeta):
    """The execution interface."""

    # --------------------------------------------------------------------------
    # LIFE CYCLE HOOK METHODS
    # --------------------------------------------------------------------------

    def __init_subclass__(cls) -> None:
        pass

    # --------------------------------------------------------------------------
    # ABSTRACT METHODS
    # --------------------------------------------------------------------------

    @abstractmethod
    def run(
        self,
        **kwargs: Any,
    ) -> Either[ExecutionError, ExecuteResponse]:
        raise NotImplementedError


# ------------------------------------------------------------------------------
# SETUP DEFAULT EXPORTS
# ------------------------------------------------------------------------------


__all__ = [
    "CreateResponse",
    "GetOrCreateResponse",
    "FetchResponse",
    "FetchManyResponse",
    "UpdateResponse",
    "UpdateManyResponse",
    "DeleteResponse",
    "ExecuteResponse",
    "Fetching",
    "Registration",
    "Updating",
    "Deletion",
    "ExecuteStep",
]
