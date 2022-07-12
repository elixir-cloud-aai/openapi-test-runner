from compliance_suite.models.v1_0_specs import *

# YAML Constants

VERSION_INFO = {
    'v1.0': 'v1',
    'v1.1': 'v1'
}

# API Constants

ENDPOINT_TO_MODEL = {
    'service_info': TesServiceInfo,
    'list_tasks_MINIMAL': TesListTasksResponseMinimal
}

REQUEST_HEADERS = {
    'Accept': 'application/json'
}
API_ENDPOINTS = {
    'SERVICE_INFO_API': 'v1/service-info'
}