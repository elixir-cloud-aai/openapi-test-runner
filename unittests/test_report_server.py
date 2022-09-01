"""Module unittests.test_report_server.py

This module is to test the Report Server class and its methods
"""

import os
import unittest
from unittest.mock import (
    MagicMock,
    patch
)

from compliance_suite.report_server import ReportServer


WEB_DIR = os.path.join(os.getcwd(), "unittests", "data", "web")


class TestReportServer(unittest.TestCase):

    def test_render_html(self):
        """Asserts if successfully able to render HTML from Jinja2 templates"""

        report_server = ReportServer(web_dir=WEB_DIR)
        report_server.render_html()
        assert True

    @patch('socketserver.TCPServer')
    @patch('webbrowser.open')
    def test_start_local_server(self, mock_web, mock_serve):
        """Asserts if a local server can be started successfully"""

        mock_web.return_value = {}
        mock_serve.return_value = MagicMock()

        report_server = ReportServer(WEB_DIR)
        report_server.start_local_server(9090, 10)
        assert True

    @patch.object(ReportServer, 'render_html')
    @patch('threading.Thread')
    def test_serve_thread(self, mock_server, mock_render_html):
        """Asserts if local server can be launched in a separate thread for given uptime"""

        mock_server.return_value = MagicMock()
        mock_render_html.return_value = None

        report_server = ReportServer(web_dir=WEB_DIR)
        report_server.local_server = MagicMock()
        report_server.serve_thread(9090, 1)
        assert True

    @patch.object(ReportServer, 'render_html')
    @patch('threading.Thread')
    def test_serve_thread_keyboard_interrupt(self, mock_server, mock_render_html):
        """Asserts if local server can be launched in a separate thread for given uptime"""

        mock_server.side_effect = [KeyboardInterrupt]
        mock_render_html.return_value = None

        report_server = ReportServer(web_dir=WEB_DIR)
        report_server.local_server = MagicMock()
        report_server.serve_thread(9090, 100)

        assert True
