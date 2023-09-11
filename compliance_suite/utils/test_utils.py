"""Module compliance_suite.utils.test_utils.py

This module contains the utility functions to perform actions on test files
"""

import importlib.resources
from pathlib import Path
from typing import (
    Any,
    List,
    Union
)

from jsonschema import (
    RefResolver,
    validate,
    ValidationError
)
import yaml

from compliance_suite.constants.constants import TEST
from compliance_suite.exceptions.compliance_exception import JobValidationException
from compliance_suite.functions.log import logger


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


def load_and_validate_yaml_data(yaml_file: str, _type: str) -> Any:
    """
    Load and validate YAML data from the file with the provided schema type.

    Args:
        yaml_file: The path to the YAML file.
        _type: The type of YAML file, either "Test" or "Template".

    Returns:
        The loaded and validated YAML data.
    """

    # Load YAML data
    try:
        # yaml_data = yaml.safe_load(open(yaml_file if _type == TEST else "tmp/testdir/"+yaml_file, "r"))
        yaml_data = yaml.safe_load(open(yaml_file, "r"))
    except yaml.YAMLError as err:
        raise JobValidationException(name="YAML Error",
                                     message=f"Invalid YAML file {yaml_file}",
                                     details=err)

    # Validate YAML data with schema
    with importlib.resources.path("compliance_suite", "test_config") as dir_path:
        schema_dir_path = dir_path.resolve()
    test_schema_path = Path(schema_dir_path/"test_schema.json")
    template_schema_path = Path(schema_dir_path/"template_schema.json")
    schema_file_path = str(test_schema_path if _type == TEST else template_schema_path)
    json_schema = yaml.safe_load(open(schema_file_path, "r"))

    try:
        # Python-jsonschema does not reference local files directly
        # Refer solution from https://github.com/python-jsonschema/jsonschema/issues/98#issuecomment-105475109
        resolver = RefResolver('file:///' + str(schema_dir_path).replace("\\", "/") + '/', None)
        validate(yaml_data, json_schema, resolver=resolver)
        logger.info(f'YAML file valid for {_type}: {yaml_file}')
    except ValidationError as err:
        raise JobValidationException(name="YAML Schema Validation Error",
                                     message=f"YAML file {yaml_file} does not match the {_type} schema",
                                     details=err.message)

    return yaml_data
