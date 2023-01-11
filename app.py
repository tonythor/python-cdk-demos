#!/usr/bin/env python3
from telnetlib import DO
import aws_cdk as cdk

# from stacks.elastic_stack import ElasticContainerServiceStack
from stacks.network_stack import NetworkStack
# from stacks.sql_insert_stack import SQLInsertStack
from stacks.dedicated_vpc_stack import DedicatedVPCStack
#from stacks.db_stack import DBStack
#from stacks.task_stack import TaskStack
#from stacks.state_machine_stack import StateMachineStack
from stacks.emr_stack import EMRStack
from stacks.emr_monitor_stack import EmrMonitor

# from stacks.ami_build_stack import AMIBuildStack
# from stacks.docker_image_stack import DockerImageStack

from stacks.config_nogit import config as config

# Note1: If any of these are deployed, they should be grouped separately and deployed as nested stacks.
# Right now it's sort of ad hoc, you want to use the database, first deploy network, then db, then sqlInsert.
app = cdk.App()
 
# Note2: for stackNames, you `cdk deploy`` the names in set in here, like network stack, but we're going to overwrite
# them in the actual stacks so they are easier to identify.
 
# The VPC stack sets up your dedicated VPC for this demo.
# After you set it up, you have to MANUALLY go in and set the VPC ID, and the private_subnets in /stacks/config.py
# (Though, it's actually nogit_config.py, create that and copy your values into it.)
dicated_vpc_stack:DedicatedVPCStack =  DedicatedVPCStack(app, "dedicatedVpcStack")
network_stack:NetworkStack = NetworkStack(scope=app, construct_id="networkStack")


## Serverless Aurora DB, and a lambda function that inserts the titanic data set into that DB.
# db_stack:DBStack = DBStack(app, "dbStack", network_stack = network_stack)
# sql_insert_stack:SQLInsertStack = SQLInsertStack(app, "sqlInsertStack", network_stack = network_stack, db_stack=db_stack)

### ECS/EC2, Docker hello world image, and a state machine to launch a docker job on the ecs cluster whenever you like,
# or triggered from eventbridge. 
# TODO: there's some permission in state machine that is preventing it from actually submitting job.
# NOTE: I'm not sure I'd use this docker-build stuff in production. Seems pretty experimental. 
# elastic_stack:ElasticContainerServiceStack = ElasticContainerServiceStack(app, "elasticStack", network_stack=network_stack)
# docker_stack:DockerImageStack = DockerImageStack(app, "dockerStack", network_stack = network_stack)
# task_stack:TaskStack = TaskStack(app, "taskStack")
# state_machine_stack:StateMachineStack = StateMachineStack(app, "smStack", 
#     elastic_stack=elastic_stack, 
#     task_stack=task_stack,
#     network_stack=network_stack)


# EMR: Build a cluster, prep for sending jobs. Hasn't had jobs submitted to it yet, it was used to set
# up cloudwatch alarms for idle clusters.
emr_stack:EMRStack = EMRStack(app, "emrStack", network_stack=network_stack)
emr_mon:EmrMonitor = EmrMonitor(app, "emonStack", network_stack=network_stack)

app.synth()
