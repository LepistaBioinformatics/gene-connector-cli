from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any, Generic, NamedTuple, TypeVar

from .either import Either
from .exceptions import (
    CreationError,
    DeletionError,
    ExecutionError,
    FetchingError,
    UpdatingError,
)

# ? ----------------------------------------------------------------------------
# ? DEFAULT RESPONSE TYPES
# ? ----------------------------------------------------------------------------


T = TypeVar("T")


class CreateResponse(NamedTuple, Generic[T]):
    """A interface for creation return methods."""

    created: bool
    instance: Generic[T]  # type: ignore


class CreateManyResponse(NamedTuple, Generic[T]):
    """A interface for batch creation return methods."""

    created: bool
    instance: list[Generic[T]]  # type: ignore


class GetOrCreateResponse(NamedTuple, Generic[T]):
    """A interface for get_or_creation return methods."""

    created: bool
    instance: Generic[T]  # type: ignore


class FetchResponse(NamedTuple, Generic[T]):
    """A interface for fetch return methods."""

    fetched: bool
    instance: Generic[T] | None  # type: ignore


class FetchManyResponse(NamedTuple, Generic[T]):
    """A interface for fetch return methods."""

    fetched: bool
    instance: list[Generic[T]] | None  # type: ignore


class UpdateResponse(NamedTuple, Generic[T]):
    """A interface for update return methods."""

    updated: bool
    instance: Generic[T]  # type: ignore


class UpdateManyResponse(NamedTuple, Generic[T]):
    """A interface for update return methods."""

    updated: bool
    records: int


class DeleteResponse(NamedTuple, Generic[T]):
    """A interface for delete return methods."""

    deleted: bool
    instance: Generic[T]  # type: ignore


class ExecuteResponse(NamedTuple, Generic[T]):
    """A interface for execution return methods."""

    executed: bool
    instance: Generic[T]  # type: ignore


class Fetching(metaclass=ABCMeta):
    """The registration interface."""

    # ? ------------------------------------------------------------------------
    # ? LIFE CYCLE HOOK METHODS
    # ? ------------------------------------------------------------------------

    def __init_subclass__(cls) -> None:
        pass

    # ? ------------------------------------------------------------------------
    # ? ABSTRACT METHODS
    # ? ------------------------------------------------------------------------

    @abstractmethod
    def show(
        self,
        **kwargs: Any,
    ) -> Either[FetchingError, FetchManyResponse[Generic[T]]]:  # type: ignore
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        **kwargs: Any,
    ) -> Either[FetchingError, FetchResponse[Generic[T]]]:  # type: ignore
        raise NotImplementedError


class Registration(metaclass=ABCMeta):
    """The registration interface."""

    # ? ------------------------------------------------------------------------
    # ? LIFE CYCLE HOOK METHODS
    # ? ------------------------------------------------------------------------

    def __init_subclass__(cls) -> None:
        pass

    # ? ------------------------------------------------------------------------
    # ? ABSTRACT METHODS
    # ? ------------------------------------------------------------------------

    @abstractmethod
    def create(
        self,
        **kwargs: Any,
    ) -> Either[CreationError, CreateResponse[Generic[T]]]:  # type: ignore
        raise NotImplementedError

    @abstractmethod
    def create_many(
        self,
        **kwargs: Any,
    ) -> Either[CreationError, CreateManyResponse[Generic[T]]]:  # type: ignore
        raise NotImplementedError

    @abstractmethod
    def get_or_create(
        self,
        **kwargs: Any,
    ) -> Either[CreationError, GetOrCreateResponse[Generic[T]]]:  # type: ignore
        raise NotImplementedError


class Updating(metaclass=ABCMeta):
    """The updating interface."""

    # ? ------------------------------------------------------------------------
    # ? LIFE CYCLE HOOK METHODS
    # ? ------------------------------------------------------------------------

    def __init_subclass__(cls) -> None:
        pass

    # ? ------------------------------------------------------------------------
    # ? ABSTRACT METHODS
    # ? ------------------------------------------------------------------------

    @abstractmethod
    def update(
        self,
        **kwargs: Any,
    ) -> Either[UpdatingError, UpdateResponse[Generic[T]]]:  # type: ignore
        raise NotImplementedError


class Deletion(metaclass=ABCMeta):
    """The deletion interface."""

    # ? ------------------------------------------------------------------------
    # ? LIFE CYCLE HOOK METHODS
    # ? ------------------------------------------------------------------------

    def __init_subclass__(cls) -> None:
        pass

    # ? ------------------------------------------------------------------------
    # ? ABSTRACT METHODS
    # ? ------------------------------------------------------------------------

    @abstractmethod
    def delete(
        self,
        **kwargs: Any,
    ) -> Either[DeletionError, DeleteResponse[Generic[T]]]:  # type: ignore
        raise NotImplementedError


class ExecuteStep(metaclass=ABCMeta):
    """The execution interface."""

    # ? ------------------------------------------------------------------------
    # ? LIFE CYCLE HOOK METHODS
    # ? ------------------------------------------------------------------------

    def __init_subclass__(cls) -> None:
        pass

    # ? ------------------------------------------------------------------------
    # ? ABSTRACT METHODS
    # ? ------------------------------------------------------------------------

    @abstractmethod
    def run(
        self,
        **kwargs: Any,
    ) -> Either[ExecutionError, ExecuteResponse[Generic[T]]]:  # type: ignore
        raise NotImplementedError


# ? ----------------------------------------------------------------------------
# SETUP DEFAULT EXPORTS
# ? ----------------------------------------------------------------------------


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
