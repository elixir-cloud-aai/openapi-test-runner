#!/bin/sh

# expects 'TesEndpointUrl' to already be set, can be done in Dockerfile
# default is set to localhost
openapi-test-runner report --server $TES_ENDPOINT_URL --include-tags all --output_path results