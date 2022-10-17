from inspect import stack
from stat import ST_GID
from aws_cdk import (
    Stack,
    Duration,
    triggers,
    aws_stepfunctions_tasks as tasks,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda as ll)

# from aws_cdk.custom_resources import (
#     AwsCustomResource,
#     AwsCustomResourcePolicy,
#     PhysicalResourceId,
#     AwsSdkCall
# )

from constructs import Construct
from stacks.config import config as config
from stacks.db_stack import DBStack
from stacks.network_stack import NetworkStack

class SQLInsertStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,  db_stack: DBStack,  
                network_stack:NetworkStack, **kwargs) -> None:
        slug = config.get('slug')

        super().__init__(scope, construct_id,  stack_name=f"cf{slug}SqlInsertStack", **kwargs)

         ## The policy
        actions = [
            'ssm:DescribeParameters',
            'ssm:GetParameter',
            'logs:CreateLogGroup',
            'logs:PutLogEvents',
            'logs:CreateLogStream',
            'ec2:DescribeNetworkInterfaces',
            'ec2:CreateNetworkInterface',
            'ec2:DeleteNetworkInterface',
            'ec2:DescribeInstances',
            'ec2:AttachNetworkInterface',
            'secretsmanager:GetSecretValue',
        ]

        statement = iam.PolicyStatement(actions=actions,resources=["*"])
        policy_document =  iam.PolicyDocument(statements=[statement])
        managed_policy = iam.ManagedPolicy(self, document=policy_document, id=f"{slug}-policy")

        lambda_role = iam.Role(self, id=f"{slug}-role",
            managed_policies=[managed_policy],
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="a role created from the codebase of gitlab:hello-aws"
        )

        def layer_arn(loc:str) -> str:
            # arn:aws:lambda:us-east-1:764573855117:layer:psycopg2-2-9-3-python38-x86-64:1 
            return f"arn:aws:lambda:us-east-1:{config.get('account')}:layer:{loc}"
            

        sg:ec2.SecurityGroup = ec2.SecurityGroup(self, id=f"{config.get('slug')}SG", vpc = network_stack.vpc, allow_all_outbound=True, description=f"{config.get('slug')}")
        sg.add_ingress_rule(ec2.Peer.ipv4(config['network'].get('sn1_cider')), ec2.Port.all_tcp())
        sg.add_ingress_rule(ec2.Peer.ipv4(config['network'].get('sn2_cider')), ec2.Port.all_tcp())
        
        ## The role

        ## Layers for Lambda, so it can run postgres and python together.
        numpy_layer    = ll.LayerVersion.from_layer_version_arn(self, id="numpy_layer",  
                         layer_version_arn=layer_arn(config['lambda'].get('numpy_version')))

        pandas_layer   = ll.LayerVersion.from_layer_version_arn(self, id="pandas_layer", 
                         layer_version_arn=layer_arn(config['lambda'].get('pandas_version')))

        psycopg2_layer = ll.LayerVersion.from_layer_version_arn(self, id="psycopg2_layer",
                         layer_version_arn=layer_arn(config['lambda'].get('psycopg2_version')))

        ## The actual lambda function
        lambda_fn = ll.Function(self, id=f"{slug}-sql-insert-lambda",
            code=ll.Code.from_asset("./lambda_src"),
            handler="lambda.handler",
            memory_size=512,
            timeout=Duration.seconds(100),
            runtime=ll.Runtime.PYTHON_3_8,
            role=lambda_role,
            environment={'DB_SECRET_LOCATION': f'{db_stack.aurora.secret.secret_name}'},
            vpc=network_stack.vpc,
            security_groups=[sg],
            layers=[numpy_layer, pandas_layer, psycopg2_layer])

        # A trigger is a lambda function that runs the lambda function above when a construct is complete.
        triggers.Trigger(self, f"{slug}-populate-db-trigger", handler=lambda_fn, execute_on_handler_change=False)
