from io import StringIO
from unittest import TestCase

from pandas import read_csv
from pandera.errors import SchemaError

from gcon.core.domain.dtos.reference_data import ReferenceData


class GeneColumnSchemaTest(TestCase):
    def test_load_valid_gene_names(self) -> None:
        df = read_csv(
            StringIO(
                """
nuc-its\tmit-gapdh\tnuc-tef1\n
AC00001\tAC00002\tAC00003
                """
            ),
            sep="\t",
        )

        ReferenceData.build_genes_schema_from_list(
            genes=df.columns,
        ).validate(df)

    def test_load_invalid_gene_names(self) -> None:
        df = read_csv(
            StringIO(
                """
aits\t1apdh\tnuctef1\n
AC00001\tAC00002\tAC00003
                """
            ),
            sep="\t",
        )

        self.assertRaises(
            SchemaError,
            ReferenceData.build_genes_schema_from_list(
                genes=df.columns,
            ).validate,
            df,
        )
