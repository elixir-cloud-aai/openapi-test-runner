"""Module compliance_suite.constants.constants.py

This module contains the constant values used across the project. It is divided into suitable categories.
"""

# Utility Constants

LOGGING_LEVEL = {
    'SKIP': 15,
    'SUCCESS': 25,
    'SUMMARY': 45
}

# API Constants
# 1. Basic & Full views have same required fields. Hence, validating Basic views against Full view Model.

ENDPOINT_TO_MODEL = {
    'service_info': 'TesServiceInfo',
    'list_tasks_MINIMAL': 'TesListTasksResponseMinimal',
    'list_tasks_BASIC': 'TesListTasksResponse',
    'list_tasks_FULL': 'TesListTasksResponse',
    'get_task_MINIMAL': 'TesTaskMinimal',
    'get_task_BASIC': 'TesTask',
    'get_task_FULL': 'TesTask',
    'create_task': 'TesCreateTaskResponse',
    'create_task_request_body': 'TesTask',
    'cancel_task': 'TesCancelTaskResponse'
}

REQUEST_HEADERS = {
    'TES': {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
}
