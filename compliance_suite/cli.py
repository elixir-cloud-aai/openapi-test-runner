"""Module compliance_suite.cli.py

This module is the entry point for the compliance suite and contains a CLI functionality
"""
import os.path
from typing import List

import click

from compliance_suite.functions.log import logger
from compliance_suite.job_runner import JobRunner
from compliance_suite.report_server import ReportServer


@click.group()
def main() -> None:
    pass


@main.command(help='Run TES compliance tests against the servers')
@click.option('--tag', '-t', multiple=True, help='Tag', default=['All'])
@click.option('--output_path', '-o', help='path to output the JSON report')
@click.option('--serve', default=False, is_flag=True, help='spin up a server')
@click.option('--port', default=15800, help='port at which the compliance report is served')
@click.option('--uptime', '-u', default=3600, help='time that server will remain up in seconds')
def report(tag: List[str],
           output_path: str,
           serve: bool,
           port: int,
           uptime: int) -> None:
    """ Run the compliance suite for the given tags """

    tag = [val.lower() for val in tag]      # Convert the tags into lowercase to allow case-insensitive tags
    logger.info(f"Input tag is - {tag}")
    job_runner = JobRunner(tag)
    job_runner.run_jobs()

    json_report = job_runner.generate_report()

    if output_path is not None:
        logger.info(f"Writing JSON Report on directory {output_path}")
        with open(os.path.join(output_path, "report.json"), "w+") as output:
            output.write(json_report)

    # Writing a report copy to web dir
    with open(os.path.join(os.getcwd(), "web", "web_report.json"), "w+") as output:
        output.write(json_report)

    if serve is True:
        report_server = ReportServer(os.path.join(os.getcwd(), "web"))
        report_server.serve_thread(port, uptime)


if __name__ == "__main__":
    main()
