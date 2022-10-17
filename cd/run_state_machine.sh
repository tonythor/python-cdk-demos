#!/bin/bash

slug="slug=HelloAwsAuroraServerlessDevAfraser"
STATE_MACHINE=$(aws stepfunctions list-state-machines| jq .stateMachines[].stateMachineArn -r  |grep $slug) 
aws stepfunctions start-execution --state-machine-arn $STATE_MACHINE