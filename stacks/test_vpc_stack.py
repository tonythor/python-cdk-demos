from aws_cdk import (
    RemovalPolicy,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_logs as logs
)

from constructs import Construct
from stacks.config import config as config

class TestVPCStack(Stack):
    def __init__(self, scope: Construct, id: str):
        ## This project was designed to work with existing private subnets, edit the stacks/config.py file
        ## and you're good to go. 
        
        ## If you need a VPC, you can either use aws wizards ./doc/create_vpc.png,
        ## Or you can run this stack to create one for you. This is a NOT CONNECTED stack,
        ## It's totally independent. As well it should be moved out of the stack library 
        ## when the project is migrated over to NBC infrastructure.

        slug = config.get('slug')
        super().__init__(scope, id, stack_name=f'cf{slug}TestVpcStack',)

        flow_log_role = iam.Role(self, f"{slug}-ecsRole", 
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            role_name=f'{config.get("slug")}-vpc-flow-log-role')
            
        flow_log_actions = [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams"
        ]

        statement = iam.PolicyStatement(actions=flow_log_actions,resources=["*"])
        policy_document =  iam.PolicyDocument(statements=[statement])
        managed_policy = iam.ManagedPolicy(self, document=policy_document, id=f"{slug}-policy")
        flow_log_role.add_managed_policy(managed_policy)


        self.vpc = ec2.Vpc(self, "Vpc",
            vpc_name = f"cloudformation-{slug}",
            cidr = "10.0.0.0/16",
            enable_dns_hostnames=True,
            enable_dns_support=True,
            availability_zones = ["us-east-1a", "us-east-1b"],
            subnet_configuration = [
                ec2.SubnetConfiguration(
                    subnet_type = ec2.SubnetType.PUBLIC,
                    name = "public",
                    cidr_mask = 24,
                ),
                ec2.SubnetConfiguration(
                    subnet_type = ec2.SubnetType.PRIVATE_WITH_NAT,
                    name = "private1",
                    cidr_mask = 24,
                )
            ]
        )

        self.log_group = logs.LogGroup(self, f"CloudFormation-{slug}", log_group_name=f"cloudformation-{slug}", removal_policy=RemovalPolicy.DESTROY)

        # set up a vpc flog log for subnet troubleshooting.
        ec2.FlowLog(self, "FlowLog",
            resource_type=ec2.FlowLogResourceType.from_vpc(vpc=self.vpc),
            destination=ec2.FlowLogDestination.to_cloud_watch_logs(log_group=self.log_group, iam_role=flow_log_role)
        )

        # send to cloudwatch.
        self.vpc.add_flow_log("FlowLogCloudWatch",
            traffic_type=ec2.FlowLogTrafficType.ALL
            
        )



