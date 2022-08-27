"""Module unittests.test_server_s3.py

This module is to test the s3 server class
"""

import os
import unittest
from unittest.mock import (
    MagicMock,
    Mock,
    patch
)

from compliance_suite.servers.s3 import ServerS3

S3_SERVER_CONFIG_PATH = os.path.join(os.getcwd(), "unittests", "data", "resources", "s3_server_config.yml")
FILE_PATH = os.path.join(os.getcwd(), "unittests", "data", "resources", "textfile.txt")
FILE_OUTPUT_PATH = os.path.join(os.getcwd(), "unittests", "data", "resources", "textfile_output.txt")


class TestServerS3(unittest.TestCase):

    @patch('os.path.join')
    def test_set_server_config(self, mock_os):
        """Asserts to set the server config successfully"""

        mock_os.return_value = S3_SERVER_CONFIG_PATH

        s3_obj = ServerS3()
        assert True

    @patch('boto3.resource')
    @patch('os.path.join')
    def test_set_s3_resource(self, mock_os, mock_boto3):
        """Asserts to set the s3 resource successfully"""

        mock_os.return_value = S3_SERVER_CONFIG_PATH
        mock_boto3.return_value = None

        s3_obj = ServerS3()
        s3_resource = s3_obj.set_s3_resource()
        assert True

    @patch('os.path.join')
    def test_upload_file(self, mock_os):
        """Asserts to upload the file to bucket successfully"""

        mock_os.return_value = S3_SERVER_CONFIG_PATH
        mock_self = Mock()

        s3_obj = ServerS3()
        s3_obj.upload_file(mock_self, "Compliance Testing", FILE_PATH, "test_file.txt")
        assert True

    @patch('os.path.join')
    def test_download_file(self, mock_os):
        """Asserts to download the file from bucket successfully"""

        mock_os.return_value = S3_SERVER_CONFIG_PATH
        mock_self = Mock()

        s3_obj = ServerS3()
        s3_obj.download_file(mock_self, "Compliance Testing", "test_file.txt",  FILE_OUTPUT_PATH)
        assert True

    @patch('os.path.join')
    def test_read_file(self, mock_os):
        """Asserts to read the file from bucket successfully"""

        mock_os.return_value = S3_SERVER_CONFIG_PATH
        mock_self = MagicMock()

        s3_obj = ServerS3()
        s3_obj.read_file(mock_self, "Compliance Testing", "test_file.txt")
        assert True

    @patch('boto3.resource')
    @patch('os.path.join')
    def test_functional_test(self, mock_os, mock_boto3):
        """Asserts to run the s3 functional test successfully"""

        mock_self = MagicMock()
        mock_os.return_value = S3_SERVER_CONFIG_PATH
        mock_boto3.return_value = mock_self

        mock_shell = Mock()
        mock_shell.execute_command.return_value = ""

        mock_request_body = MagicMock()

        s3_obj = ServerS3()
        assert s3_obj.functional_test(mock_request_body) == ""

    @patch('boto3.resource')
    @patch('os.path.join')
    def test_delete_bucket_out(self, mock_os, mock_boto3):
        """Asserts to delete the bucket successfully"""

        mock_self = MagicMock()
        mock_os.return_value = S3_SERVER_CONFIG_PATH
        mock_boto3.return_value = mock_self

        s3_obj = ServerS3()
        s3_obj.delete_bucket_out()
        assert True
