from unittest import TestCase

from gcon.core.domain.dtos.metadata import (
    Metadata,
    MetadataKey,
    MetadataKeyGroup,
)


class MetadataKeyGroupsTest(TestCase):
    def test_set_key_group_method_with_own_keys(self) -> None:
        for group in MetadataKeyGroup:
            for key in group.value.keys:
                response = MetadataKeyGroup.set_key_group(key)
                self.assertEqual(response, group)

    def test_set_key_group_method_with_wrong_keys(self) -> None:
        for group in MetadataKeyGroup:
            for key in group.value.keys:
                response = MetadataKeyGroup.set_key_group(key + "not")
                self.assertEqual(response, MetadataKeyGroup.OTHER)

    def test_self_validate(self) -> None:
        MetadataKeyGroup.self_validate()


class MetadataTest(TestCase):
    def test_add_feature_method(self) -> None:
        metadata = Metadata()
        metadata.add_feature("key", "value")

        self.assertEqual(
            metadata.qualifiers,
            {
                MetadataKey(
                    group=MetadataKeyGroup.OTHER,
                    key="key",
                ): "value"
            },
        )

    def test_add_feature_method_with_valid_organism(self) -> None:
        metadata = Metadata()
        metadata.add_feature("organism", "value")

        self.assertEqual(
            metadata.qualifiers,
            {
                MetadataKey(
                    group=MetadataKeyGroup.TAXONOMY,
                    key="organism",
                ): "value"
            },
        )
