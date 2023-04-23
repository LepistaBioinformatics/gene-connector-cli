from os import getenv
from pathlib import Path
from unittest import TestCase

from gcon.core.domain.dtos.reference_data import ReferenceData


class ReferenceDataTest(TestCase):
    def setUp(self) -> None:
        valid_source_table_env_path = getenv("PARSED_REFERENCE_DATA_JSON")
        valid_source_table_path = Path(str(valid_source_table_env_path))
        self.assertTrue(valid_source_table_path.is_file())

        self.__parsed_ref_data = valid_source_table_path

    def test_load_from_json_with_valid_data(self) -> None:
        response_either = ReferenceData.from_json(
            json_path=self.__parsed_ref_data,
        )

        self.assertTrue(response_either.is_right)
        self.assertIsInstance(response_either.value, ReferenceData)
