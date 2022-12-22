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


