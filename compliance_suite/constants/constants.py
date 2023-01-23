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

import compliance_suite.models.v1_1_specs as v1_1
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
    'v1.0': {
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
    },
    'v1.1': {
        'service_info': v1_1.TesServiceInfo,
        'list_tasks_MINIMAL': v1_1.TesListTasksResponseMinimal,
        'list_tasks_BASIC': v1_1.TesListTasksResponse,
        'list_tasks_FULL': v1_1.TesListTasksResponse,
        'get_task_MINIMAL': v1_1.TesTaskMinimal,
        'get_task_BASIC': v1_1.TesTask,
        'get_task_FULL': v1_1.TesTask,
        'create_task': v1_1.TesCreateTaskResponse,
        'create_task_request_body': v1_1.TesTask,
        'cancel_task': v1_1.TesCancelTaskResponse
    }
}

REQUEST_HEADERS = {
    'TES': {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
}
