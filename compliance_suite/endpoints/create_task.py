import requests
import jsonschema
import json

REQUEST_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

LIST_TASKS_API = 'v1/tasks'


def create_task(server_url):

    base_url = str(server_url) + LIST_TASKS_API
    print(f"Hitting endpoint - {base_url}")
    with open("examples/requests/post-create-task-body.json") as file:
        request_body = json.load(file)
    print(f"Request Body - {request_body}")

    with open("schemas/requests/post-create-task-body.json") as file:
        request_body_schema = json.load(file)
    try:
        jsonschema.validate(request_body, request_body_schema)
        print(f"Successful Request Body Schema Validation")
    except jsonschema.ValidationError as err:
        print(err.message)

    response = requests.post(base_url, headers=REQUEST_HEADERS, json=request_body)
    response_json = response.json()
    print(f"Response - {response.status_code} | {response_json} ")

    if response.status_code == 200:
        print(f"Successful request")
    else:
        print("Request Failed. Incorrect Response Status Code.")

    with open("schemas/responses/post-create-task.json") as file:
        schema_json = json.load(file)
    try:
        jsonschema.validate(response_json, schema_json)
        print(f"Successful Response Schema Validation")
    except jsonschema.ValidationError as err:
        print(err.message)
