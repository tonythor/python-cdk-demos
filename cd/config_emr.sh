#!/bin/bash
## needs to be up on S3 just like this, is for EMR bootstrapping
## make sure the config_emr.json is up there too! 
sudo yum install amazon-cloudwatch-agent -y
sudo amazon-linux-extras install collectd -y
aws s3 cp s3://tonyfraser-admin/cloudwatch-agent/config_emr.json /home/hadoop/config.json
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:///home/hadoop/config.json