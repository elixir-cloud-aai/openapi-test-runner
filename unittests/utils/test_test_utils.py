"""Module unittests.utils.test_test_utils.py

This module is to test the TestUtils class and its methods
"""

from compliance_suite.utils.test_utils import TestUtils


class TestTestUtils:

    def test_tag_matcher_success(self):
        """Test the tag_matcher function for a successful match"""
        assert TestUtils.tag_matcher(["tag"], [], ["tag", "tag1"]) is True

    def test_tag_matcher_fail(self):
        """Test the tag_matcher function for a failed match"""
        assert TestUtils.tag_matcher(["tag"], ["tag"], ["tag", "tag1"]) is False

    def test_version_matcher_success(self):
        """Test the version_matcher function for a successful match"""
        assert TestUtils.version_matcher("1.0.0", ["1.0.0", "1.1.0"]) is True

    def test_version_matcher_fail(self):
        """Test the version_matcher function for a failed match"""
        assert TestUtils.version_matcher("2.0.0", ["1.0.0", "1.1.0"]) is False
