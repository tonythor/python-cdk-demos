## Ami's with SSM and the Cloudwatch agent   
High level, seems logical to me that every server launched for any reason should have two things that it currently doesn't. First, it should be sending metrics and system logs to cloud watch and second it should be hooked into SSM from the start. There should be no SSH key rotation, local users, any of that. Any administration or auditing can and should come via SSM.

Turns out, it's pretty easy to do, and there are two different ways of doing it. 
We'll discuss two in this document.

### Prereqs:
1. If you're trying ot get SSM and/or cloudwatch up on any box, either managed service or not, the role that the machine runs as needs a couple IAM policies attached to the execution role. Check the EMR stack in this project for the exact ones. You're probably also going to need that role to have S3 access to something, because that's where the bootstrap script and jars are going to be .
1. Second, SSM and CW both require client daemons. There are several ways to get here, but check the bootstrap script in the demo, or install the components by EC2 Image builder.


### Bootstrapping SSM/CW into an instance at the EC2 layer. 
In [emr_stack.py](../stacks/emr_stack.py) there is an example of how to use bootstrap to get all this running. The emr stack initializes, and then runs a bootstrap that installs a couple of components on top, and then gets a cw-agent-client config file that sends EMR metrics and log files.

This can method can be used for _any_ ec2 instance, fargate, standalone ec2, beanstalk, whatever. 

### Building an AMI image with these components preinstalled:
Let's say you want to speed up your ec2 startup time, either on EMR, or standalone, or whatever. You can pre-build your AMI with these components, and then just launch the AMI.

#### Build your recipe

1. Go search AMI Builder on the console, create a new recipe that has the following:
    1. Components:
        1. amazon-cloudwatch-agent-linux
        1. aws-cli-version-2-linux
        1. python3-linux
        1. amazon-corretto-11
    1. Set your version, like 0.0.1
    1. Add this into user data: 
        * Do NOT yum update!!
        * TODO: Figure out how to add S3 access to EC2 Image Builder role

```
#!/bin/bash
## needs to be up on S3 just like this, is for EMR bootstrapping
## make sure the config_emr.json is up there too! 
sudo yum install amazon-cloudwatch-agent -y
sudo amazon-linux-extras install collectd -y
aws s3 cp s3://tonyfraser-admin/cloudwatch-agent/config_emr.json /home/hadoop/config.json
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:///home/hadoop/config.json
```

## build your pipeline, test your instance
    1. Load the recipe in the pipelines console, look for "create a pipeline for this recipe". This section talks about that wizard.
        * when done, the output goes to your personal AMI's, like in launch instance -> My AMI's
        * also, sends logs and keystrokes to cloudwatch
        * also allows you to connect directly to box with `aws ssm start-session --target {running instance id}`
    2. Setup SSM keystroke logging for all ECS instances:
        Console -> AWS Systems Manager -> Cloudwatch Logging -> Enable and send to  /logging/sessionmanager-keystrokes
    3. Create an IAM role with:
        * S3 Full Access (or at least to the config file bucket)
        * CloudWatchAgentServerPolicy
        * AmazonSSMManagedInstanceCore
    4. Go to EC2->Launch instance
        1. Pick you "my AMI"
        1. No key pair, you're going to use SSM to connect
        1. Set your private vpc and private subnet
        1. Security group doesn't need any permissions, should have no permissions
        3. Go into "advacned advanced and apply the IAM role to it.    
    4. Connect to your instance and test
        * use ssm and start a sesson, make sure you can access.
        * verify keystroke logging
        * verify whatever log files from the host you are sending to cloudwatch
      
* Note: if your logging doesn't start correctly, SSM into the box, run the "aws s3 cp logconfig.json" and amazon-cloudwatch-agent-ctl reinitialize bit. It whatever role built the image probaby didn't have permission to access your S3 bucket. 

### Notes: 
* You can now use your custom instance anywhere, and it's pre-bootstrapped with these two components. Pretty any cluster, emr, ecs, etc, all have flags for custom-ami-instance. 
* aws session-manager requires a client to be installed locally, which is covered in the main readme for this demo.

