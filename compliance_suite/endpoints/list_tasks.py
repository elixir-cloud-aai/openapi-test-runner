import requests
import jsonschema
import json

REQUEST_HEADERS = {
    'Accept': 'application/json'
}
LIST_TASKS_API = 'v1/tasks'


def list_tasks_full(server_url):

    base_url = str(server_url) + LIST_TASKS_API
    print(f"Hitting endpoint - {base_url}")
    query_params = {'view': 'FULL'}
    response = requests.get(base_url, headers=REQUEST_HEADERS, params=query_params)
    response_json = response.json()
    print(f"Response - {response.status_code} | {response_json} ")

    if response.status_code == 200:
        print(f"Successful request")
    else:
        print("Request Failed. Incorrect Response Status Code.")

    with open("schemas/responses/get-list_tasks-full.json") as file:
        schema_json = json.load(file)
    try:
        jsonschema.validate(response_json, schema_json)
        print(f"Successful Response Schema Validation")
    except jsonschema.ValidationError as err:
        print(err.message)


def list_tasks_basic(server_url):

    base_url = str(server_url) + LIST_TASKS_API
    print(f"Hitting endpoint - {base_url}")
    query_params = {'view': 'BASIC'}
    response = requests.get(base_url, headers=REQUEST_HEADERS, params=query_params)
    response_json = response.json()
    print(f"Response - {response.status_code} | {response_json} ")

    if response.status_code == 200:
        print(f"Successful request")
    else:
        print("Request Failed. Incorrect Response Status Code.")

    with open("schemas/responses/get-list_tasks-basic.json") as file:
        schema_json = json.load(file)
    try:
        jsonschema.validate(response_json, schema_json)
        print(f"Successful Response Schema Validation")
    except jsonschema.ValidationError as err:
        print(err.message)


def list_tasks_minimal(server_url):

    base_url = str(server_url) + LIST_TASKS_API
    print(f"Hitting endpoint - {base_url}")
    query_params = {'view': 'MINIMAL'}
    response = requests.get(base_url, headers=REQUEST_HEADERS, params=query_params)
    response_json = response.json()
    print(f"Response - {response.status_code} | {response_json} ")

    if response.status_code == 200:
        print(f"Successful request")
    else:
        print("Request Failed. Incorrect Response Status Code.")

    with open("schemas/responses/get-list_tasks-minimal.json") as file:
        schema_json = json.load(file)
    try:
        jsonschema.validate(response_json, schema_json)
        print(f"Successful Response Schema Validation")
    except jsonschema.ValidationError as err:
        print(err.message)








