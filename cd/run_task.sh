#!/bin/bash

# will allow outbound traffic from subnet,but no inbound traffic.
security_group=sg-0e63adaa08d3eee1f 
subnet1=subnet-0e96b0da7960f966e  # these will be two private subnets, natted to the outside world
subnet2=subnet-0ead34bf6358d7e5a
region=us-east-1

# this is from config.py and used to look up the docker image.
slug=HelloAwsAuroraServerlessDevAfraser
task_def_name=$slug

account=$(aws sts get-caller-identity |jq -r .Account)
cluster_name=$(aws ecs list-clusters  |grep $slug | awk '{split($0,a,"/"); print a[2]}' |sed "s:\"::g")
cluster=arn:aws:ecs:$region:$account:cluster/$cluster_name


## Task definition information
## by default, uses the most recently deployed task
# task_def_number=10
task_def_number=$(aws ecs list-task-definitions |grep $slug |tail -1 |sed 's/[\",\,]//g' |  awk '{split($0,a,":"); print a[7];}')
task_def=$task_def_name:$task_def_number


# launch the task, note to simplify networking
# this is set to launch into your public subnet
network_config='{
  "awsvpcConfiguration": {
    "securityGroups": ["'$security_group'"],
    "subnets": ["'$subnet1'"]
  }
}'

cmd="aws ecs run-task \
    --task-definition $task_def \
    --cluster $cluster \
    --launch-type EC2 \
    --network-configuration '$network_config'"

echo $cmd
eval "$cmd"