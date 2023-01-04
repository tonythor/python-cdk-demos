# python-cdk-demos


Set up this project:
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
```


## setup session manager locally
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/mac/sessionmanager-bundle.zip" -o "sessionmanager-bundle.zip" 
unzip sessionmanager-bundle.zip
sudo ./sessionmanager-bundle/install -i /usr/local/sessionmanagerplugin -b /usr/local/bin/session-manager-plugin
aws ec2 describe-instances > ./running_instances.json
aws ssm start-session --target {instance-id from json}
