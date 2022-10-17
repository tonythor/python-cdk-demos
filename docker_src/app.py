from pg_wrapper import PGWrapper
from secrets_wrapper import SecretsWrapper
import os
import json
import boto3
import botocore
import urllib3

def boto_get_s3_file(bucket, key):
   # note -> no credentials, boto automatically checks the ECS environment variable 
   # AWS_CONTAINER_CREDENTIALS_RELATIVE_URI. See pypi://botocore/credentials.py
   s3 = boto3.client("s3")
   s3_object = s3.get_object(Bucket=bucket, Key=key)
   return s3_object['Body'].read().decode('utf-8') 

def http_get_data(http, url, to_json=False):
   # for demonstrating what's happening in the ecs environment
   resp = http.request('GET', url)
   if to_json:
      return json.loads(resp.data.decode('utf-8'))
   else:
      return resp.data.decode('utf-8')

def running_on_ecs() -> bool:
   if  os.environ.get("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI"):
      return True
   else:
      return False


if __name__ == '__main__':
   print()
   print("**************************************************")
   print("demo data here -> s3://nbcuas-contextual/env/it/titanic_head_5.csv")
   print("*************** inbound arguments ****************")
   print(f"inbound sys.argv arguments: {len(sys.argv)}")
   for i, arg in enumerate(sys.argv):
        print(f"inbound argument {i} : {i:>6}: {arg}")
   print()
   print()
   print("****** s3 load file using boto *******************")
   print(boto_get_s3_file(bucket = 'nbcuas-contextual', key='env/it/titanic_head_5.csv'))
   print()
   print()
   print("********* shell environment variables ************")
   for k, v in os.environ.items():
      print(f'{k}={v}')
   print()
   print()
  
   if running_on_ecs():
      print("************ ecs url variables *******************")  
      http = urllib3.PoolManager()
      AWS_CONTAINER_CREDENTIALS_RELATIVE_URI = os.environ.get("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI")
      ECS_CONTAINER_METADATA_URI_V4=os.environ.get("ECS_CONTAINER_METADATA_URI_V4")
      ECS_CONTAINER_METADATA_URI=os.environ.get("ECS_CONTAINER_METADATA_URI_V4")
      ip=ECS_CONTAINER_METADATA_URI_V4.split("/")[2]  
      print("** HTTP GET of ECS_CONTAINER_METADATA_URI_V4")
      print(http_get_data(http = http, url=ECS_CONTAINER_METADATA_URI_V4))
      print("** HTTP GET of ECS_CONTAINER_METADATA_URI")
      print(http_get_data(http = http, url=ECS_CONTAINER_METADATA_URI))
      print("** HTTP GET of AWS_CONTAINER_CREDENTIALS_RELATIVE_URI")
      print(http_get_data(http=http, url=f"{ip}{AWS_CONTAINER_CREDENTIALS_RELATIVE_URI}", to_json=True))
      print("*************************************************")   

