import re
from typing import Literal

from bibtexparser import loads as bib_loads
from numpy import nan
from pandera import (
    Check,
    Column,
    DataFrameModel,
    DataFrameSchema,
    Field,
)
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


def __check_accession(accessions: str) -> Literal[True]:
    """Check if the accessions are valid.

    Args:
        accessions (str): A list of accessions.

    Returns:
        Literal[True]: True if the accessions are valid.

    Raises:
        ValueError: If the accessions are not valid.

    """

    def validate_single_accession(accession: str) -> Literal[True]:
        """Validate a single accession.

        Args:
            accession (str): A single accession.

        Returns:
            Literal[True]: True if the accession is valid.

        Raises:
            ValueError: If the accession is not valid.

        """

        nucleotide = re.compile(r"^[A-Z]{1,2}_?[0-9]{5,8}$")
        protein = re.compile(r"^[A-Z]{3}[0-9]{5,7}$")
        wgs = re.compile(r"^[A-Z]{4,6}[0-9]{2}[0-9]{6,7}$")
        mga = re.compile(r"^[A-Z]{5}[0-9]{7}$")

        for name, pattern in [
            ("protein", protein),
            ("wgs", wgs),
            ("mga", mga),
        ]:
            if re.findall(pattern, accession):
                raise ValueError(
                    f"Accession is a {name} ({pattern}). Only nucleotides are "
                    + f"allowed ({nucleotide})"
                )

        if not re.findall(nucleotide, accession):
            raise ValueError(
                f"Invalid nucleotide format of accession `{accession}` ({nucleotide})."
            )

        return True

    if len(accessions) == 0:
        return True

    for accession in accessions:
        if accession is nan:
            continue

        if isinstance(accession, str):
            accession = accession.split(",")  # type: ignore

        accession_splitted = [i.strip() for i in accession if i]

        for accession in accession_splitted:
            validate_single_accession(accession)

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


GeneColumnSchema = (
    Column,
    "^[a-z]{3}-[a-zA-Z0-9]+$",
    dict(
        # dtype=str,
        regex=True,
        required=True,
        nullable=True,
        checks=[Check(lambda i: __check_accession(i))],
    ),
)
