#!/usr/bin/env python3
from telnetlib import DO
import aws_cdk as cdk

from stacks.config import config
from stacks.elastic_stack import ElasticContainerServiceStack
from stacks.network_stack import NetworkStack
from stacks.db_stack import DBStack
from stacks.task_stack import TaskStack
from stacks.state_machine_stack import StateMachineStack
from stacks.sql_insert_stack import SQLInsertStack
from stacks.test_vpc_stack import TestVPCStack
from stacks.docker_image_stack import DockerImageStack

from stacks.config import config as config

# Note1: If any of these are deployed, they should be grouped separately and deployed as nested stacks.
# Right now it's sort of ad hoc, you want to use the database, first deploy network, then db, then sqlInsert.
app = cdk.App()
 

# Note2: for stackNames, you `cdk deploy`` the names in set in here, like network stack, but we're going to overwrite
# them in the actual stacks so they are easier to identify.
 
# REQUIRED: This sets up your network. It loads whatever you set in /stacks/config.py for subnets and VPC's.
network_stack:NetworkStack = NetworkStack(scope=app, construct_id="networkStack")

# A serverless aurora db, and a lambda function that inserts the titanic data set into that DB.
db_stack:DBStack = DBStack(app, "dbStack", network_stack = network_stack)
sql_insert_stack:SQLInsertStack = SQLInsertStack(app, "sqlInsertStack", network_stack = network_stack, db_stack=db_stack)

# An ec2/ecs cluster, and a prebuilt hello world docker container as a runnable state machine so you can keep firing 
# off that docker container into ecs as often as you want.

#first push the docker stack
elastic_stack:ElasticContainerServiceStack = ElasticContainerServiceStack(app, "elasticStack", network_stack=network_stack)
docker_stack:DockerImageStack = DockerImageStack(app, "dockerStack", network_stack = network_stack)
task_stack:TaskStack = TaskStack(app, "taskStack")
state_machine_stack:StateMachineStack = StateMachineStack(app, "smStack", 
    elastic_stack=elastic_stack, 
    task_stack=task_stack,
    network_stack=network_stack)

# a stack that BUILDS a vpc. Not required, but one of three ways to kick off using these templates.
# see the testVPC stack file. You will have to uncomment this out to use it.
test_vpc_stack: TestVPCStack(app, "testVpcStack")


app.synth()
