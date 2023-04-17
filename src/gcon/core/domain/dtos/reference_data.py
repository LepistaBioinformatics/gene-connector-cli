from attrs import define
from pandera import DataFrameModel, Field
from pandera.typing import Series


@define(kw_only=True)
class Citation:
    ...


class StandardFieldsSchema(DataFrameModel):
    identifier: Series[str] = Field(alias="Identifier", unique=True)
    sci_name: Series[str] = Field(alias="ScientificName")
    literature: Series[str] = Field(alias="Literature")


@define(kw_only=True)
class ReferenceData:
    # ? ------------------------------------------------------------------------
    # ? CLASS ATTRIBUTES
    # ? ------------------------------------------------------------------------

    ...
