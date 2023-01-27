#!/bin/sh

# This file proves to be less useful if the url of the server never changes and all tests are always run
# If tests need to be run in a specific order
# or only specific tests need to be run this file allows for that to be adjusted
# If the server url is not constant it can be passed into as a variable
# or if basic auth is used and a username/password are required to run the tests

# example command below
# tes-compliance-suite report --server <insert_url> --tag all --output_path results