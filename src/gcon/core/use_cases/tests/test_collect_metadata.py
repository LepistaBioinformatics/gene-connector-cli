from os import getenv
from pathlib import Path
from unittest import TestCase

from pandas import read_csv

from gcon.core.domain.dtos.reference_data import ReferenceData
from gcon.core.use_cases.collect_metadata import collect_metadata


class CollectMetadataTest(TestCase):
    def setUp(self) -> None:
        valid_source_table_env_path = getenv("VALID_REFERENCE_TABLE")
        valid_source_table_path = Path(str(valid_source_table_env_path))
        self.assertTrue(valid_source_table_path.is_file())

        valid_source_table_path = valid_source_table_path
        content_rows = read_csv(valid_source_table_path, sep="\t")
        content_rows.drop(0, inplace=True)

        self.__reference_data = ReferenceData(
            data=content_rows,
            optional_fields=[],
            gene_fields=["nuc-its", "mit-gapdh", "nuc-tef1"],
        )

    def test_collect_metadata(self) -> None:
        metadata = collect_metadata(
            reference_data=self.__reference_data,
            output_dir_path=Path("/tmp"),
        )

        self.assertTrue(metadata.is_right)
        self.assertIsInstance(metadata.value, ReferenceData)
        self.assertEqual(len(metadata.value.connections), 4)
