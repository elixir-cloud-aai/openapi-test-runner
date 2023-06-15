"""Module unittests.utils.test_test_utils.py

This module is to test the TestUtils class and its methods
"""

from compliance_suite.utils.test_utils import tag_matcher


class TestTestUtils:

    def test_tag_matcher_success(self):
        """Test the tag_matcher function for a successful match"""
        assert tag_matcher(["tag"], [], ["tag", "tag1"]) is True

    def test_tag_matcher_fail(self):
        """Test the tag_matcher function for a failed match"""
        assert tag_matcher(["tag"], ["tag"], ["tag", "tag1"]) is False
