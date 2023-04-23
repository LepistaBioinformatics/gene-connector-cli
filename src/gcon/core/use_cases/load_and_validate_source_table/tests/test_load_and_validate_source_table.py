from os import getenv
from pathlib import Path
from unittest import TestCase

from gcon.core.domain.dtos.reference_data import ReferenceData
from gcon.core.domain.utils.either import Either
from gcon.core.domain.utils.exceptions import UseCaseError
from gcon.core.use_cases.load_and_validate_source_table import (
    load_and_validate_source_table,
)


class LoadAndValidateSourceTableTest(TestCase):
    def setUp(self) -> None:
        valid_source_table_env_path = getenv("VALID_REFERENCE_TABLE")
        valid_source_table_path = Path(str(valid_source_table_env_path))
        self.assertTrue(valid_source_table_path.is_file())

        self.__valid_source_table_path = valid_source_table_path

        invalid_source_table_env_path = getenv("INVALID_REFERENCE_TABLE")
        invalid_source_table_path = Path(str(invalid_source_table_env_path))
        self.assertTrue(invalid_source_table_path.is_file())

        self.__invalid_source_table_path = invalid_source_table_path

    def test_load_and_validate_source_table_with_valid_data(self) -> None:
        response: Either = load_and_validate_source_table(
            source_table_path=self.__valid_source_table_path
        )

        self.assertTrue(response.is_right)
        self.assertFalse(response.is_left)
        self.assertIsInstance(response.value, ReferenceData)

    def test_load_and_validate_source_table_with_invalid_data(self) -> None:
        response: Either = load_and_validate_source_table(
            source_table_path=self.__invalid_source_table_path
        )

        self.assertFalse(response.is_right)
        self.assertTrue(response.is_left)
        self.assertIsInstance(response.value, UseCaseError)


if __name__ == "__main__":
    from unittest import main

    main()
