"""Module compliance_suite.constants.constants.py

This module contains the constant values used across the project. It is divided into suitable categories.
"""

from compliance_suite.models.v1_0_specs import (
    TesCancelTaskResponse,
    TesCreateTaskResponse,
    TesListTasksResponse,
    TesListTasksResponseMinimal,
    TesServiceInfo,
    TesTask,
    TesTaskMinimal,
)

# YAML Constants

VERSION_INFO = {
    'v1.0': 'v1',
    'v1.1': 'v1'
}

# Utility Constants

LOGGING_LEVEL = {
    'SKIP': 15,
    'SUCCESS': 25,
    'SUMMARY': 45
}

# API Constants

ENDPOINT_TO_MODEL = {
    'service_info': TesServiceInfo,
    'list_tasks_MINIMAL': TesListTasksResponseMinimal,
    'list_tasks_BASIC': TesListTasksResponse,
    'list_tasks_FULL': TesListTasksResponse,
    'get_task_MINIMAL': TesTaskMinimal,
    'get_task_BASIC': TesTask,
    'get_task_FULL': TesTask,
    'create_task': TesCreateTaskResponse,
    'create_task_request_body': TesTask,
    'cancel_task': TesCancelTaskResponse
}

REQUEST_HEADERS = {
    'TES': {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
}
