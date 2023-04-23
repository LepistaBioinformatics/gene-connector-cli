from copy import deepcopy
from os import getenv
from pathlib import Path
from unittest import TestCase

from gcon.core.domain.dtos.reference_data import ReferenceData
from gcon.core.domain.dtos.score import ConnectionScores
from gcon.core.use_cases.build_metadata_match_scores import (
    build_metadata_match_scores,
)


class BuildMetadataMatchScoresTest(TestCase):
    def setUp(self) -> None:
        valid_source_table_env_path = getenv("PARSED_REFERENCE_DATA_JSON")
        valid_source_table_path = Path(str(valid_source_table_env_path))
        self.assertTrue(valid_source_table_path.is_file())

        response_either = ReferenceData.from_json(
            json_path=valid_source_table_path,
        )

        self.assertTrue(response_either.is_right)
        self.assertIsInstance(response_either.value, ReferenceData)

        self.__ref_data = response_either.value

    def test_build_metadata_match_scores(self) -> None:
        response = build_metadata_match_scores(
            reference_data=deepcopy(self.__ref_data),
        )

        self.assertTrue(response.is_right)
        self.assertIsInstance(response.value, ReferenceData)

        for connection in response.value.connections:
            self.assertIsInstance(connection.scores, ConnectionScores)
