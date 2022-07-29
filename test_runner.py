import json
from pydantic import ValidationError
from compliance_suite.functions.requestor import send_request, poll_request
from compliance_suite.constants.constants import VERSION_INFO, ENDPOINT_TO_MODEL
from compliance_suite.functions.colored_console import print_blue, print_red, print_green


class TestRunner():

    def __init__(self, server, version):

        self.server = server
        self.version = VERSION_INFO[version]
        self.job_data = None
        self.auxiliary_space = {}

    def validate_logic(self, endpoint_model, json_data, message):

        try:
            ENDPOINT_TO_MODEL[endpoint_model](**json_data)
            print_green(f'{message} Schema validation |successful| for {self.job_data["operation"]} {self.job_data["endpoint"]}')
        except ValidationError as err:
            print_red(f'{message} Schema validation |failed| for {self.job_data["operation"]} {self.job_data["endpoint"]}')
            print(err)

    def validate_request_body(self, request_body):

        request_body_json = None

        # JSON Validation
        try:
            request_body_json = json.loads(request_body)
        except json.JSONDecodeError as err:
            print_red(f"Error in request body - {err}")

        # Logical Schema Validation

        endpoint_model = self.job_data["name"] + "_request_body"
        self.validate_logic(endpoint_model, request_body_json, "Request Body")

    def validate_response(self, response):

        # General status validation
        response_status = list(self.job_data["response"].keys())[0]
        if response.status_code == response_status:
            print(f"Successful request")
        else:
            print_red("Request Failed. Incorrect Response Status Code.")

        # Logical Schema Validation
        if not response.text:
            response_json = {}
        else:
            response_json = response.json()
        # print(response_json)

        if self.job_data["name"] in ["list_tasks", "get_task"]:
            view_query = [item["view"] for item in self.job_data["query_parameters"]]
            endpoint_model = self.job_data["name"] + "_" + view_query[0]
        else:
            endpoint_model = self.job_data["name"]
        self.validate_logic(endpoint_model, response_json, "Response")
        self.auxiliary_space[self.job_data["name"]] = response_json

    def run_tests(self, job_data):

        # print(job_data)
        self.job_data = job_data

        id_uri_param = None
        query_params = {}
        request_body = None

        if job_data["name"] in ["get_task", "cancel_task"]:
            id_uri_param = self.auxiliary_space["create_task"]["id"]

        if job_data["name"] in ["get_task", "list_tasks"]:
            for param in job_data["query_parameters"]:
                query_params.update(param)
            # print(query_params)

        if job_data["name"] in ["create_task"]:
            request_body = job_data["request_body"]
            self.validate_request_body(request_body)
            # print(request_body)

        if "polling" in job_data.keys():

            check_cancel = False
            # print(self.auxiliary_space)
            if "cancel_task" in self.auxiliary_space.keys():
                check_cancel = True

            response = poll_request(self.server, self.version, job_data["endpoint"],
                                id_uri_param, query_params, job_data["operation"], job_data["polling"]["interval"],
                                job_data["polling"]["timeout"], check_cancel)
        else:
            response = send_request(self.server, self.version, job_data["endpoint"],
                                id_uri_param, query_params, job_data["operation"], request_body)

        self.validate_response(response)

