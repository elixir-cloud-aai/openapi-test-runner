"""Module compliance_suite.utils.test_utils.py

This module contains the utility functions to perform actions on test files
"""

from typing import List


def tag_matcher(
        include_tags: List[str],
        exclude_tags: List[str],
        yaml_tags: List[str]
) -> bool:
    """ Checks if the given conditions are met based on the provided tags. Skips the test if tag is not matched.

    Args:
        include_tags: User-provided list of tags for which the compliance suite will be run
        exclude_tags: User-provided list of tags for which the compliance suite will not be run
        yaml_tags: The tags defined for a YAML test file

    Returns:
        True if none of exclude_tags match any of the yaml_tags, and at least one of the include_tags is
        present in the yaml_tags. Otherwise, False.
    """

    # If include_tags is empty, all tests are considered included

    return (
        not any(exclude_tag in yaml_tags for exclude_tag in exclude_tags)
        and (not include_tags or any(include_tag in yaml_tags for include_tag in include_tags))
    )
