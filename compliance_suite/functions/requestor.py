import json

import requests
from compliance_suite.constants.constants import *


def send_request(server, version, endpoint, id_uri_param, operation, request_body):

    if id_uri_param:
        endpoint = endpoint.replace("{id}", id_uri_param)

    base_url = str(server) + version + endpoint
    response = None
    print(f"Sending {operation} request to {base_url}")
    if operation == "GET":
        response = requests.get(base_url, headers=REQUEST_HEADERS)
    elif operation == "POST":
        if request_body:
            request_body = json.loads(request_body)
            response = requests.post(base_url, headers=REQUEST_HEADERS, json=request_body)
        else:
            response = requests.post(base_url, headers=REQUEST_HEADERS)
    return response
