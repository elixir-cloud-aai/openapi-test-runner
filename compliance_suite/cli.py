"""Module compliance_suite.cli.py

This module is the entry point for the compliance suite and contains a CLI functionality
"""

from typing import List

import click

from compliance_suite.functions.log import logger
from compliance_suite.job_runner import JobRunner


@click.group()
def main() -> None:
    pass


@main.command(help='Run TES compliance tests against the servers')
@click.option('--tag', '-t', multiple=True, help='Tag', default=['All'])
def report(tag: List[str]) -> None:
    """ Run the compliance suite for the given tags """

    tag = [val.lower() for val in tag]      # Convert the tags into lowercase to allow case-insensitive tags
    logger.info(f"Input tag is - {tag}")
    job_runner = JobRunner(tag)
    job_runner.run_jobs()


if __name__ == "__main__":
    main()
