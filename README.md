# python-cdk-demos
## Overview
This is my working project where I practice with Python CDK. There are all sorts of examples in here, including:
* Building a custom VPC from scratch
* Creating a network construct 
* Creating an Aurora DB, and prepopulating that with the Titanic data set.
* Creating an EC2/ECS cluster and using state machine to send jobs to it.
* Creating an EMR cluster (but one that specifically launches with SSM and the cloud watch agent) 
etc.

If you want to try any of these, you might need to comment some in our out of [./app.py](./app.py)

## Set up this project:
```
## git clone
python3 -m venv .venv     # build your project virtual env 
source .venv/bin/activate # activate your virual env
.venv/bin/python -m pip install --upgrade pip 
.venv/bin/python -m pip install -r ./requirements.txt
```

To run:
```
cdk synth
cdk deploy dedicatedVPCStack
## go get subnet id's and vpc id from console, put them in config.py
cdk deploy networkStack
cdk deploy {whichever stack you want to play with}
```


## Extra: 
### Set up session manager locally
```
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/mac/sessionmanager-bundle.zip" -o "sessionmanager-bundle.zip" 
unzip sessionmanager-bundle.zip
sudo ./sessionmanager-bundle/install -i /usr/local/sessionmanagerplugin -b /usr/local/bin/session-manager-plugin
aws ec2 describe-instances > ./running_instances.json
aws ssm start-session --target {instance-id from json}
```

### Custom AMI's
* TODO: a stack that builds an ami
* [launch ami with cloudwatch and ssm](./doc/amis_with_ssm_and_cloudwatch.md)