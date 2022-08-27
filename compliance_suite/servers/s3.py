"""Module compliance_suite.servers.s3.py

This module contains class definition for S3 Server to perform actions on TES S3 Storage
"""


import os
import time
from typing import Any

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import yaml

from compliance_suite.exceptions.compliance_exception import (
    JobValidationException,
    TestRunnerException
)
from compliance_suite.functions.log import logger
from compliance_suite.functions.shell_executor import ShellExecutor


class ServerS3():

    def __init__(self):

        self.server_url: str = ""
        self.username: str = ""
        self.password: str = ""
        self.region_name: Any = None

        self.set_server_config()

    def set_server_config(self) -> None:
        """Extract the server config values and assign them to class data members"""

        config_path: str = os.path.join(os.getcwd(), "resources", "server_config.yml")
        with open(config_path, "r") as f:
            server_config = yaml.safe_load(f)

        if server_config["server_url"] == "None" or server_config["username"] == "None" or \
                server_config["password"] == "None":
            raise JobValidationException(name="S3 Exception", message="Insufficient server config details provided",
                                         details=None)
        self.server_url = server_config["server_url"]
        self.username = server_config["username"]
        self.password = server_config["password"]

        if server_config["region_name"] != "None":
            self.region_name = server_config["region_name"]

    def set_s3_resource(self) -> Any:
        """Function used to set the s3 resource which will be used further to perform s3 actions"""

        print(f'{self.server_url}, {self.username}, {self.password}, {self.region_name}')
        return boto3.resource(service_name='s3',
                              endpoint_url=self.server_url,
                              aws_access_key_id=self.username,
                              aws_secret_access_key=self.password,
                              region_name=self.region_name,
                              config=Config(signature_version='s3v4'))

    def upload_file(
            self,
            s3_res: Any,
            bucket_name: str,
            local_file_path: str,
            s3_file_path: str
    ) -> None:
        """Function used to upload a local file at local_file_path to bucket - bucket_name with the
        Key - s3_file_path"""

        try:
            s3_res.create_bucket(Bucket=bucket_name)
            logger.info(f"New bucket - {bucket_name} created")
            time.sleep(10)  # Need some time to reflect the new bucket
            input_file = open(local_file_path, 'rb')
            s3_res.Bucket(bucket_name).put_object(Key=s3_file_path, Body=input_file)
            logger.info(f"File {local_file_path} uploaded to {bucket_name}")

        except ClientError as err:
            raise TestRunnerException(name="S3 Exception",
                                      message=f"Unable to upload file - {local_file_path} to bucket - {bucket_name}",
                                      details=err)

    def download_file(
            self,
            s3_res: Any,
            bucket_name: str,
            s3_file_path: str,
            local_output_path: str
    ) -> None:
        """ Used to download files or read large sized files. Downloads Key - s3_file_path in bucket - bucket_name
         at the local path - local_output_path"""
        try:
            s3_res.Bucket(bucket_name).download_file(Key=s3_file_path, Filename=local_output_path)
            logger.info(f'Key - {s3_file_path} in bucket - {bucket_name} downloaded at {local_output_path}')
        except ClientError as err:
            raise TestRunnerException(name="S3 Exception",
                                      message=f"Unable to download file - {s3_file_path} from bucket - {bucket_name} ",
                                      details=err)

    def read_file(
            self,
            s3_res: Any,
            bucket_name: str,
            s3_file_path: str
    ) -> str:
        """Read the file content from Key - s3_file_path in bucket - bucket_name"""
        try:
            logger.info(f'Reading data from Key - {s3_file_path} in bucket - {bucket_name}')
            return s3_res.Object(bucket_name, s3_file_path).get()["Body"].read().decode("utf-8")
        except ClientError as err:
            raise TestRunnerException(name="S3 Exception",
                                      message=f"Unable to read file - {s3_file_path} in bucket - {bucket_name}",
                                      details=err)

    def delete_bucket(
            self,
            s3_res: Any,
            bucket_name: str
    ) -> None:
        """Delete the bucket - bucket_name and all the objects inside it"""
        try:
            for obj in s3_res.Bucket(bucket_name).objects.all():
                obj.delete()
            s3_res.Bucket(bucket_name).delete()
            logger.info(f"Bucket {bucket_name} deleted successfully")
        except ClientError as err:
            raise TestRunnerException(name="S3 Exception", message="Unable to delete S3 bucket", details=err)

    def functional_test(
            self,
            request_body_json: Any
    ) -> Any:
        """Perform functional test. Create a new bucket, then upload a file. Get the expected output by running
        a shell executor which mimics the TES server behaviour. Return this expected output to be compared with
        actual TES server response for validation"""

        s3_res = self.set_s3_resource()

        file_url: str = request_body_json["inputs"][0]["url"][5:]  # Remove "s3:// prefix"
        bucket_name: str = file_url.split("/")[0]
        local_file_path: str = "resources/" + file_url.split("/")[-1]
        s3_file_path: str = file_url.split("/")[-1]

        # Upload a file
        self.upload_file(s3_res, bucket_name, local_file_path, s3_file_path)

        # Getting expected response from Shell Executor
        shell_obj = ShellExecutor()
        command_file_path = request_body_json["inputs"][0]["path"]
        executor_data: Any = shell_obj.execute_command(command=request_body_json["executors"][0]["command"],
                                                       command_file_path=command_file_path,
                                                       local_file_path=local_file_path)

        return executor_data

    def delete_bucket_out(self) -> None:
        """Delete the bucket. Called from test-runner.py. TODO Make it parameterized"""

        s3_res = self.set_s3_resource()

        logger.info(f"Deleting bucket - compliance_testing")
        self.delete_bucket(s3_res, "compliance-testing")
