#!/bin/sh

# expects 'TesEndpointUrl' to already be set, can be done in Dockerfile
# default is set to localhost
tes-compliance-suite report --server $TES_ENDPOINT_URL --tag all --output_path results