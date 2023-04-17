from os import getenv
from pathlib import Path
from unittest import TestCase

from gcon.core.use_cases.load_and_sanitize_data.load_and_validate_source_table import (
    load_and_validate_source_table,
)


class LoadAndValidateSourceTableTest(TestCase):
    def setUp(self) -> None:
        source_table_env_path = getenv("REFERENCE_TABLE")
        source_table_path = Path(str(source_table_env_path))
        self.assertTrue(source_table_path.is_file())

        self.__source_table_path = source_table_path

    def test_load_and_validate_source_table(self) -> None:
        load_and_validate_source_table(source_table=self.__source_table_path)


if __name__ == "__main__":
    from unittest import main

    main()
