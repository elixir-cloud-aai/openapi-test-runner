"""Module compliance_suite.suite_validator.py

This module contains class definition for Suite Validator to validate the tests, templates and models present in the
test suite repository
"""

import ast
from pathlib import Path

from compliance_suite.constants.constants import (
    TEMPLATE,
    TEST
)
from compliance_suite.exceptions.compliance_exception import JobValidationException
from compliance_suite.functions.log import logger
from compliance_suite.utils.test_utils import load_and_validate_yaml_data


class SuiteValidator:
    """Class to validate the test suite"""

    @staticmethod
    def check_directory(directory_path: Path, directory_type: str):
        """Check if the directory exists and contains required files. Validate the file format and schema"""

        if not directory_path.exists() and directory_path.is_dir():
            raise JobValidationException(name="Validation failed",
                                         message=f"Required directory {directory_type} not present in the test suite",
                                         details="NULL")

        files = list(directory_path.glob("*specs.py" if directory_type == "models" else "*.yml"))

        if not files:
            raise JobValidationException(
                name="Validation failed",
                message=f"No files present within {directory_type} directory inside test suite",
                details="NULL")

        for file in files:
            if directory_type == "tests":
                load_and_validate_yaml_data(str(file), TEST)
            elif directory_type == "templates":
                load_and_validate_yaml_data(str(file), TEMPLATE)
            else:
                try:
                    with file.open('r') as f:
                        ast.parse(f.read())
                    logger.info(f"Python file valid for Model: {f.name}")
                except SyntaxError as err:
                    logger.error(f"Syntax error in model file {f.name}")
                    raise JobValidationException(
                        name="Validation failed",
                        message=f"Invalid model file {f.name}",
                        details=err.__str__())

    @staticmethod
    def validate():
        """Performs multiple validation checks on the test suite"""

        project_root_dir = Path.cwd().resolve()
        required_directories = ["models", "tests", "templates"]

        try:
            for directory_type in required_directories:
                directory_path = project_root_dir / directory_type
                SuiteValidator.check_directory(directory_path, directory_type)

        except JobValidationException as err:
            logger.error("Test suite validation failed.")
            logger.error(err)
