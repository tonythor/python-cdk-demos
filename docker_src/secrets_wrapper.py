from botocore.exceptions import ClientError
import boto3
import json

class SecretsWrapper:
    """ a wrapper for secrets manager that returns a dict of just the [SecretString]"""
 
    def __init__(self, 
            region:str = 'us-east-1', 
            account='396600302754'):
        self.region = region    
        self.secret_arn = f"arn:aws:secretsmanager:{region}:{account}:secret"

    def get_rds_secret(self, secret:str) -> dict:
        """ this is the rds specific secret type """
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=self.region
        )

        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=f"{self.secret_arn}:{secret}"
            )
            
            return json.loads(get_secret_value_response['SecretString'])
        except ClientError as e:
            # too many exception types to sort on, just throw an exception.
            raise e
    
    def get_aws_secret(self, secret:str) -> dict:
        """ this is the rds specific secret type """
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=self.region
        )

        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=f"{self.secret_arn}:{secret}"
            )
            
            return json.loads(get_secret_value_response['SecretString'])
        except ClientError as e:
            # too many exception types to sort on, just throw an exception.
            raise e
