import requests
import jsonschema
import json

# TODO - Add proper schema and validate
# Add check for empty response

REQUEST_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

LIST_TASKS_API = 'v1/tasks/'
TASK_ID = 'task-8cdb11f9'
CANCEL_API = ':cancel'


def cancel_task(server_url):

    base_url = str(server_url) + LIST_TASKS_API + TASK_ID + CANCEL_API
    print(f"Hitting endpoint - {base_url}")
    response = requests.post(base_url, headers=REQUEST_HEADERS)

    print(f"Response - {response.status_code}")

    if response.status_code == 200:
        print(f"Successful request")
    else:
        print("Request Failed. Incorrect Response Status Code.")

    if len(response.text) == 0:
        print(f"Successful Validation")
    else:
        print(f"Validation Failed. ")

