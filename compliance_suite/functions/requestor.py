import json
import requests
from compliance_suite.constants.constants import REQUEST_HEADERS
import polling2
from compliance_suite.exceptions.ComplianceException import ComplianceException

check_cancel = None


def send_request(server, version, endpoint, id_uri_param, query_params, operation, request_body):
    if id_uri_param:
        endpoint = endpoint.replace("{id}", id_uri_param)

    base_url = str(server) + version + endpoint
    response = None
    print(f"Sending {operation} request to {base_url}. Query Parameters - {query_params}")
    if operation == "GET":
        if query_params:
            response = requests.get(base_url, headers=REQUEST_HEADERS, params=query_params)
        else:
            response = requests.get(base_url, headers=REQUEST_HEADERS)
    elif operation == "POST":
        if request_body:
            request_body = json.loads(request_body)
            response = requests.post(base_url, headers=REQUEST_HEADERS, json=request_body)
        else:
            response = requests.post(base_url, headers=REQUEST_HEADERS)
    return response


def poll_callback(response):
    return check_poll(response, check_cancel)


def check_poll(response, check_cancel):

    if response.status_code != 200:
        print("Unexpected response from Polling request. Retrying...")
        return False

    response_json = response.json()
    if check_cancel and response_json["state"] in ["CANCELED"]:
        print("Expected response received. Polling request successful")
        return True

    elif not check_cancel and response_json["state"] in ["COMPLETE", "EXECUTOR_ERROR", "SYSTEM_ERROR"]:
        print("Expected response received. Polling request successful")
        return True

    print("Unexpected response from Polling request. Retrying...")
    return False


def poll_request(server, version, endpoint, id_uri_param, query_params, operation,
                 polling_interval, polling_timeout, check_cancel_val):

    endpoint = endpoint.replace("{id}", id_uri_param)
    global check_cancel
    check_cancel = check_cancel_val
    base_url = str(server) + version + endpoint
    response = None
    print(f"Sending {operation} polling request to {base_url}. Query Parameters - {query_params}")
    if operation == "GET":

        try:
            response = polling2.poll(lambda: requests.get(base_url, headers=REQUEST_HEADERS, params=query_params),
                                     step=polling_interval, timeout=polling_timeout,
                                     check_success=poll_callback)
        except polling2.TimeoutException:
            raise ComplianceException(f"Polling timeout for {operation} {base_url}")
    return response
