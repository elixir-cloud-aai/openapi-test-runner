from compliance_suite.models.v1_0_specs import *

# YAML Constants

VERSION_INFO = {
    'v1.0': 'v1',
    'v1.1': 'v1'
}

# API Constants

ENDPOINT_TO_MODEL = {
    'service_info': TesServiceInfo,
    'list_tasks_MINIMAL': TesListTasksResponseMinimal,
    'list_tasks_BASIC': TesListTasksResponse,
    'list_tasks_FULL': TesListTasksResponse,
    'get_task_MINIMAL': TesTaskMinimal,
    'get_task_BASIC': TesTask,
    'get_task_FULL': TesTask
}

REQUEST_HEADERS = {
    'Accept': 'application/json'
}
API_ENDPOINTS = {
    'SERVICE_INFO_API': 'v1/service-info'
}