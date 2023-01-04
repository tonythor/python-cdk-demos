## Creating and running a custom AMI   
In an effort to correctly capture logging and SSM on ec2 instance, either as part of an emr or load balanced ecs cluster, I'm putting this little hidden gem into this project.

### Setup
1. Set up your network: I've been using this dedicatedVPCStack and networkStack in this project.
1. Go search AMI Builder on the console, create a new recipe that has the following:
    1. Components:
        1. amazon-cloudwatchh-agent-linux
        1. aws-cli-version-2-linux
        1. python3-linux
        1. amazon-corretto-11
    1. Add this into userdata, do NOT yum update!! (config.json is in this directory for reference 
    
``` #!/usr/bin/bash
sudo yum install mlocate awscli amazon-cloudwatch-agent  -y 
sudo mkdir -p sudo mkdir -p /opt/aws/amazon-cloudwatch-agent/bin/

aws s3 cp s3://tonyfraser-admin/cloudwatch-agent/config.json  /tmp/amazon-cloudwatch-agent.json
sudo cp /tmp/amazon-cloudwatch-agent.json /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json

# sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json


# sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json

sudo /bin/updatedb
sudo systemctl enable amazon-ssm-agent
sudo systemctl enable amazon-cloudwatch-agent
sudo systemctl start amazon-ssm-agent
sudo systemctl start amazon-cloudwatch-agent ```

    1. Set a version, save the recipe.
    1. Load the recipe in the console, look for "create a pipeline for this recipe" and go through that.
    1. Run the pipline, that'll get you your image in launch image -> my ami's.
    1. Setup SSM keystroke logging for all ECS instances:
        console -> AWS Systems Manager -> Cloudwatch Logging -> Enable and send to  /logging/sessionmanager-keystrokes
    1. Add an IAM role with
        1. S3 Full Access (or at least to the config file bucket)
        1. CloudWatchAgentServerPolicy
        1. AmazonSSMManagedInstanceCore
    1. Go to EC2->Launch instance
        1. Pick you AMI
        1. No key pair, you're going to use SSM to connect
        1. Set the private vpc and private subnet
        1. Security group doesn't need any permissions
        3. Make sure you go into advanced and apply the IAM role to it.    



https://aws.amazon.com/premiumsupport/knowledge-center/emr-custom-metrics-cloudwatch/

#!/bin/bash

sudo yum install amazon-cloudwatch-agent -y
sudo amazon-linux-extras install collectd -y

aws s3 cp <s3 path for config.json> /home/hadoop/config.json

sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:///home/hadoop/config.json
