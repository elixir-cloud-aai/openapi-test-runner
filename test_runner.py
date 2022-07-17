import json
from pydantic import ValidationError
from compliance_suite.functions.requestor import send_request
from compliance_suite.constants.constants import VERSION_INFO, ENDPOINT_TO_MODEL


class TestRunner():

    def __init__(self, server, version):

        self.server = server
        self.version = VERSION_INFO[version]
        self.job_data = None
        self.auxiliary_space = {}

    def validate_request_body(self, request_body):

        request_body_json = None

        # JSON Validation
        try:
            request_body_json = json.loads(request_body)
        except json.JSONDecodeError as err:
            print(f"Error in request body - {err}")

        # Logical Schema Validation
        try:
            endpoint_model = self.job_data["name"] + "_request_body"

            ENDPOINT_TO_MODEL[endpoint_model](**request_body_json)
            print(f'Request Body Schema validation successful for {self.job_data["endpoint"]}')
        except ValidationError as err:
            print(err)

    def validate_response(self, response):

        # General status validation
        response_status = list(self.job_data["response"].keys())[0]
        if response.status_code == response_status:
            print(f"Successful request")
        else:
            print("Request Failed. Incorrect Response Status Code.")

        # Logical Schema Validation

        response_json = response.json()
        # print(response_json)

        try:
            endpoint_model = None
            if self.job_data["name"] in ["list_tasks", "get_task"]:
                view_query = [item["view"] for item in self.job_data["query_parameters"]]
                endpoint_model = self.job_data["name"] + "_" + view_query[0]
            else:
                endpoint_model = self.job_data["name"]

            ENDPOINT_TO_MODEL[endpoint_model](**response_json)
            print(f'Response Schema validation successful for {self.job_data["operation"]} {self.job_data["endpoint"]}')

            self.auxiliary_space[self.job_data["name"]] = response_json
            # print(self.auxiliary_space)
        except ValidationError as err:
            print(err)

    def run_tests(self, job_data):

        # print(job_data)
        self.job_data = job_data

        id_uri_param = None
        request_body = None
        if job_data["name"] in ["get_task"]:
            id_uri_param = self.auxiliary_space["list_tasks"]["tasks"][0]["id"]
            # print(id_uri_param)
        elif job_data["name"] in ["cancel_task"]:
            id_uri_param = self.auxiliary_space["list_tasks"]["tasks"][0]["id"]
            # print(id_uri_param)
        elif job_data["name"] in ["create_task"]:
            request_body = job_data["request_body"]
            self.validate_request_body(request_body)
            # print(request_body)

        response = send_request(self.server, self.version, job_data["endpoint"],
                                id_uri_param, job_data["operation"], request_body)
        self.validate_response(response)

