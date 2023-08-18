"""Module compliance_suite.utils.test_utils.py

This module contains the utility functions to perform actions on test files
"""

from typing import (
    Any,
    List,
    Union
)


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


def replace_string(data: Any, search_str: str, replace_str: Union[str, int]) -> Any:
    """Replace all occurrences of `search_str` in `data` with `replace_str`.

    Args:
        data: The data to be processed.
        search_str: The string to search for.
        replace_str: The string to replace the occurrences with.

    Returns:
        The data with the replacements made.
    """

    if isinstance(data, list):
        for index, item in enumerate(data):
            data[index] = replace_string(item, search_str, replace_str)
        return data
    elif isinstance(data, dict):
        for key, value in data.items():
            data[key] = replace_string(value, search_str, replace_str)
        return data
    elif isinstance(data, str) or isinstance(data, int):
        return replace_str if data == search_str else data
