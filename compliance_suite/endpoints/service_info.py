import requests
import jsonschema
import json

REQUEST_HEADERS = {
    'Accept': 'application/json'
}
SERVICE_INFO_API = 'v1/service-info'


def get_service_info(server_url):

    base_url = str(server_url) + SERVICE_INFO_API
    print(f"Hitting endpoint - {base_url}")
    response = requests.get(base_url, headers=REQUEST_HEADERS)
    response_json = response.json()
    print(f"Response - {response.status_code} | {response_json} ")
    with open("schemas/responses/get-service_info.json") as file:
        schema_json = json.load(file)

    if response.status_code == 200:
        print(f"Successful request")
    else:
        print("Request Failed. Incorrect Response Status Code.")

    try:
        jsonschema.validate(response_json, schema_json)
    except jsonschema.ValidationError as err:
        print(err.message)



