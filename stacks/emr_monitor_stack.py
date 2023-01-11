from operator import sub
from re import L

from aws_cdk import (
    Stack,
    Duration,
    aws_emr as emr,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda as ll)
from constructs import Construct

from stacks.config_nogit import config as config
from stacks.network_stack import NetworkStack

class EmrMonitor(Stack):

    def __init__( self, scope: Construct, id: str, network_stack, **kwargs) -> None:
        slug = config.get('slug')
        super().__init__(scope, id, **kwargs)

        actions = [
            'ec2:DescribeNetworkInterfaces',
            'ec2:CreateNetworkInterface',
            'ec2:DeleteNetworkInterface',
            'ec2:DescribeInstances',
            'ec2:AttachNetworkInterface',
            'elasticloadbalancing:*',
            'cloudwatch:*',
            'autoscaling:*',
            'logs:CreateLogStream',
            'elasticmapreduce:ListClusters',
            'elasticmapreduce:DescribeCluster'
        ]

        statement = iam.PolicyStatement(actions=actions,resources=["*"])
        policy_document =  iam.PolicyDocument(statements=[statement])
        managed_policy = iam.ManagedPolicy(self, document=policy_document, id=f"{slug}-policy")

        lambda_role = iam.Role(self, id=f"{slug}-emr-monitor-role",
            managed_policies=[managed_policy],
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="a CF stack that monitors EMR clusters"
        )

        sg:ec2.SecurityGroup = ec2.SecurityGroup(self, id=f"{config.get('slug')}-emrMonitorSG", vpc = network_stack.vpc, allow_all_outbound=True, description=f"{config.get('slug')}")
        sg.add_ingress_rule(ec2.Peer.ipv4(config['network'].get('sn1_cider')), ec2.Port.all_tcp())
        sg.add_ingress_rule(ec2.Peer.ipv4(config['network'].get('sn2_cider')), ec2.Port.all_tcp())

        lambda_fn = ll.Function(self, id=f"{slug}-emr-monitor-lambda",
            code=ll.Code.from_asset("./lambda_src"),
            handler="lambda_emr.handler",
            memory_size=512,
            timeout=Duration.seconds(100),
            runtime=ll.Runtime.PYTHON_3_7,
            role=lambda_role,
            vpc=network_stack.vpc,
            security_groups=[sg])
   