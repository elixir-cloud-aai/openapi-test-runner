"""Module compliance_suite.report_server.py

This module contains class definition for Report Server which reads the JSON compliance report and displays it in
a webview via a local server
"""

import datetime
import http.server
import json
import os
import shutil
import socketserver
import threading
import time
from typing import (
    Any,
    List
)
import webbrowser

import jinja2 as j2

from compliance_suite.functions.log import logger
from pathlib import Path


class ReportServer():
    """Class containing the methods to serve the report via webview locally"""

    def __init__(self, web_dir: str, versions: List[str], name: str):
        """Initialize the Report Server object

        Args:
            web_dir (str): The location of web directory inside the project
        """

        self.cwd: str = os.getcwd()     # Store the current location
        self.local_server: Any = None
        self.web_dir: str = web_dir
        self.versions: List[str] = versions
        self.name = name

    def render_html(self) -> None:
        """Renders HTML dynamically at runtime via Jinja2 templates"""

        for version in self.versions:
            with open(os.path.join(self.web_dir, f"web_report-{self.name}-{version}.json"), "r") as f:
                report_data = json.load(f)

            # Render the HTML via Jinja templates
            view_loader = j2.FileSystemLoader(searchpath=self.web_dir)
            view_env = j2.Environment(loader=view_loader)
            date = datetime.datetime.utcnow().isoformat(timespec="seconds")
            report_template = view_env.get_template("views/report.html")
            report_rendered = report_template.render(data=report_data, version=version,
                                                     versions=self.versions, name=self.name, date=date)

            with open(os.path.join(self.web_dir, f"report-{self.name}-{version}.html"), "w+") as output:
                output.write(report_rendered)

        # Copy the latest test report to the default landing page
        latest_version = sorted(self.versions)[-1]
        shutil.copyfile(Path(self.web_dir, f"report-{self.name}-{latest_version}.html"),
                        Path(self.web_dir, "index.html"))

    def start_local_server(
            self,
            port: int,
            uptime: int
    ) -> None:
        """Runs a local server to serve the JSON compliance report

        Args:
            port (int): Port on which the local server will run
            uptime (int): Server uptime in seconds unless its shutdown by user
        """

        os.chdir(self.web_dir)
        http_handler = http.server.SimpleHTTPRequestHandler
        self.local_server = socketserver.TCPServer(("", port), http_handler)
        logger.info(f"Starting a local server at  http://localhost:{port}")
        webbrowser.open(f"http://localhost:{port}/index.html")
        logger.info(f"Server will shut down after {uptime} seconds, press CTRL+C to shut down manually")
        self.local_server.serve_forever()

    def serve_thread(
            self,
            port: int,
            uptime: int
    ) -> None:
        """Server is launched on a separate thread allowing it to be stopped from outside

        Args:
            port (int): Port on which the local server will run
            uptime (int): Server uptime in seconds unless its shutdown by user
        """

        try:
            self.render_html()
            server_thread = threading.Thread(target=self.start_local_server, args=(port, uptime,))
            server_thread.start()
            time.sleep(uptime)
        except KeyboardInterrupt:
            logger.info("Stopping server via Keyboard Interruption")
        finally:
            logger.info("Shutting down server as time limit reached")
            self.local_server.shutdown()
            os.chdir(self.cwd)
