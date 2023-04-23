from typing import Any

from attrs import field, frozen
from pandas import DataFrame
from pandera import DataFrameModel, Field
from pandera.typing import Series

from gcon.core.domain.dtos.connection import Connection


class StandardFieldsSchema(DataFrameModel):
    identifier: Series[str] = Field(alias="identifier", unique=True)
    sci_name: Series[str] = Field(alias="scientificName")


class OptionalFieldsSchema(DataFrameModel):
    literature: Series[str] = Field(alias="literature")


@frozen(kw_only=True)
class ReferenceData:
    """ReferenceData class.

    Attributes:
        data (DataFrame): The data table content.
        optional_fields (list[str]): A list of optional fields present in data.
        gene_fields (list[str]): A list of gene fields present in data.
        connections (list[Connection]): A list of connections present in data.

    Methods:
        with_connections: Add a list of connections to the reference data.
        to_dict: Convert the reference data to a dictionary.

    """

    # ? ------------------------------------------------------------------------
    # ? CLASS ATTRIBUTES
    # ? ------------------------------------------------------------------------

    # The data table content
    data: DataFrame = field()

    # A list of optional fields present in data
    optional_fields: list[str] = field(default=list())

    # A list of gene fields present in data
    gene_fields: list[str] = field(default=list())

    # A list of connections present in data
    connections: list[Connection] = field(init=False)

    # ? ------------------------------------------------------------------------
    # ? VALIDATORS AND DEFAULTS
    # ? ------------------------------------------------------------------------

    @connections.default
    def _set_default_connections(self) -> list[Connection]:
        return list()

    # ? ------------------------------------------------------------------------
    # ? PUBLIC INSTANCE METHODS
    # ? ------------------------------------------------------------------------

    def with_connections(self, connections: list[Connection]) -> None:
        """Add a list of connections to the reference data.

        Args:
            connections (list[Connection]): The list of connections to add.

        """

        self.connections.extend(connections)

    def to_dict(self) -> dict[str, Any]:
        """Convert the reference data to a dictionary.

        Returns:
            dict[str, list[dict[str, list[str]]]]: The reference data as a
                dictionary.

        """

        return {
            "data": self.data.to_dict(orient="records"),
            "optional_fields": self.optional_fields,
            "gene_fields": self.gene_fields,
            "connections": [
                connection.to_dict() for connection in self.connections
            ],
        }
