import requests
from compliance_suite.constants.constants import *


def send_request(server, version, endpoint, operation):
    base_url = str(server) + version + endpoint
    response = None
    print(f"Sending {operation} request to {base_url}")
    if operation == "GET":
        response = requests.get(base_url, headers=REQUEST_HEADERS)

    return response
