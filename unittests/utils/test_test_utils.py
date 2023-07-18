"""Module unittests.utils.test_test_utils.py

This module is to test the TestUtils class and its methods
"""

from compliance_suite.utils.test_utils import (
    replace_string,
    tag_matcher
)


class TestTestUtils:

    def test_tag_matcher_success(self):
        """Test the tag_matcher function for a successful match"""
        assert tag_matcher(["tag"], [], ["tag", "tag1"]) is True

    def test_tag_matcher_fail(self):
        """Test the tag_matcher function for a failed match"""
        assert tag_matcher(["tag"], ["tag"], ["tag", "tag1"]) is False

    def test_replace_string(self):
        """Tests the replace_string function for a composite data containing strings, lists and dictionaries  """

        data = [
            {
                "key1": "value1"
            },
            [
                "item1",
                "item2"
            ],
            "lorem_ipsum"
        ]

        data = replace_string(data, "item2", "item5")
        assert data[1][1] == "item5"
