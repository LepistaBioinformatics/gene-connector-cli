from bibtexparser import loads as bib_loads
from pandera import Column, DataFrameModel, DataFrameSchema, Field, Check
from pandera.typing import Series


class StandardFieldsSchema(DataFrameModel):
    identifier: Series[str] = Field(alias="identifier", unique=True)
    sci_name: Series[str] = Field(alias="scientificName")


def __check_bid(bibs: str) -> bool:
    """Load a list of bibs.

    Args:
        bibs (str): A list of bibs.

    Returns:
        bool: True if the bibs are valid.

    Raises:
        ValueError: If the bibs are not valid.

    """

    if len(bibs) == 0:
        return True

    for bib in bibs:
        try:
            libs = bib_loads(bib)

            if not libs.entries:
                raise ValueError("Bib is empty")

            for entry in libs.entries:
                if any(
                    [
                        entry.get("ID") is None,
                        entry.get("ENTRYTYPE") is None,
                        entry.get("author") is None,
                        entry.get("title") is None,
                        entry.get("year") is None,
                    ]
                ):
                    raise ValueError(
                        "Bib is missing ENTRYTYPE/author/title/year"
                    )

        except Exception as e:
            raise e

    return True


OptionalColumnsSchema = DataFrameSchema(
    {
        "literature": Column(
            str,
            required=False,
            nullable=True,
            checks=[Check(lambda i: __check_bid(i))],
        )
    }
)


GeneColumnSchema = Column(
    str,
    required=False,
    nullable=True,
    checks=[Check(lambda i: __check_bid(i))],
)
