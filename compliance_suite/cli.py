"""Module compliance_suite.cli.py

This module is the entry point for the compliance suite and contains a CLI functionality
"""

import importlib
import os
from pathlib import Path
import re
from typing import (
    Any,
    List
)

import click

from compliance_suite.constants import constants
from compliance_suite.functions.log import logger
from compliance_suite.job_runner import JobRunner
from compliance_suite.report_server import ReportServer


@click.group()
def main() -> None:
    pass


def validate_regex(ctx: Any, param: Any, value: List[str]):
    """Validate the regex for CLI arguments

    Args:
        ctx: The current click context
        param: The click parameter
        value: The value to validate

    Returns:
        The validated value if it passes the regular expression pattern.
    """

    regex_pattern: str = r"^[a-zA-Z0-9_]+$"

    if not value or all(re.fullmatch(regex_pattern, val) for val in value):
        return value
    else:
        raise click.BadParameter("Only letters (a-z, A-Z), digits (0-9) and underscores (_) are allowed.")


def set_service_constants(ctx: Any, param: Any, value: str):
    # TODO

    if value == "TES":
        constants_module_path = constants.TES_TESTS_DIR.replace("/", ".") + "constants.constants"
        service_constants_module = importlib.import_module(constants_module_path)
        service_constants = getattr(service_constants_module, "SERVICE_CONSTANTS")
        constants.SERVICE_CONSTANTS = service_constants

    return value


def transform_test_path(ctx: Any, param: Any, value: List[str]):
    # TODO

    if ctx.params['service'] == "TES" and value == ("tests",):
        modified_value = [constants.TES_TESTS_DIR + value[0]]
        return modified_value

    return value

@main.command(help='Run TES compliance tests against the servers')
@click.option('--service', '-sv', required=True, type=str,
              help='the API service name to refer the compliance tests', callback=set_service_constants) #TODO
@click.option('--server', '-s', required=True, type=str, prompt="Enter server",
              help='server URL on which the compliance tests are run. Format - https://<url>/')
@click.option('--version', '-v', required=True, type=str, prompt="Enter version",
              help='API version. Example - "1.0.0"')
@click.option('--include-tags', '-i', 'include_tags', multiple=True,
              help='run tests for provided tags', callback=validate_regex)
@click.option('--exclude-tags', '-e', 'exclude_tags', multiple=True,
              help='skip tests for provided tags', callback=validate_regex)
@click.option('--test-path', '-tp', 'test_path', multiple=True,
              help='the absolute or relative path of the tests to be run', default=["tests"],
              callback=transform_test_path)
@click.option('--output_path', '-o', help='path to output the JSON report')
@click.option('--serve', default=False, is_flag=True, help='spin up a server')
@click.option('--port', default=15800, help='port at which the compliance report is served')
@click.option('--uptime', '-u', default=3600, help='time that server will remain up in seconds')
def report(service: str,
           server: str,
           version: str,
           include_tags: List[str],
           exclude_tags: List[str],
           test_path: List[str],
           output_path: str,
           serve: bool,
           port: int,
           uptime: int) -> None:
    """ Program entrypoint called via "report" in CLI.
    Run the compliance suite for the given tags.

    Args:
        service: The API service name to refer the compliance tests
        server (str): The server URL on which the compliance suite will be run. Format - https://<url>/
        version (str): The compliance suite will be run against this API version. Example - "1.0.0"
        include_tags (List[str]): The list of the tags for which the compliance suite will be run.
        exclude_tags (List[str]): The list of the tags for which the compliance suite will not be run.
        test_path: The list of absolute or relative paths from the project root of the test file/directory.
            Default - ["tests"]
        output_path (str): The output path to store the JSON compliance report
        serve (bool): If true, runs a local server and displays the JSON report in webview
        port (int): Set the local server port. Default - 16800
        uptime (int): The local server duration in seconds. Default - 3600 seconds
    """

    for path in test_path:
        if not Path(path).exists():
            raise FileNotFoundError(f"Test path: {path} not found. Please provide a valid path.")

    # Convert the tags into lowercase to allow case-insensitive tags
    include_tags = [val.lower() for val in include_tags]
    exclude_tags = [val.lower() for val in exclude_tags]

    logger.info(f"Provided service: {service} server: {server} version: {version}")
    logger.info(f"Provided tags - include: {include_tags} exclude: {exclude_tags}")
    logger.info(f"Provided test path: {test_path}")
    job_runner = JobRunner(server, version)
    job_runner.set_tags(include_tags, exclude_tags)
    job_runner.set_test_path(test_path)
    job_runner.run_jobs()

    json_report = job_runner.generate_report()

    # Store the report in given output path
    if output_path is not None:
        logger.info(f"Writing JSON Report on directory {output_path}")
        with open(os.path.join(output_path, "report.json"), "w+") as output:
            output.write(json_report)

    # Writing a report copy to web dir for local server
    with open(os.path.join(os.getcwd(), "compliance_suite", "web", "web_report.json"), "w+") as output:
        output.write(json_report)

    if serve is True:
        report_server = ReportServer(os.path.join(os.getcwd(), "compliance_suite", "web"))
        report_server.serve_thread(port, uptime)


if __name__ == "__main__":
    main()
