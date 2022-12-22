from operator import sub
from aws_cdk import (
    Duration, Stack,
    CfnOutput,
    aws_iam as iam,
    aws_rds as rds,
    aws_ec2 as ec2, 
    aws_secretsmanager as sm
)
from constructs import Construct
from stacks.config_nogit import config as config


class NetworkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:        
        slug = config.get('slug')
        env={
            'account': config.get('account'),         
            'region': config.get('region')
        }
        super().__init__(scope, construct_id, env=env,  stack_name=f"cf{slug}NetworkStack", **kwargs)

        self.vpc:ec2.Vpc = ec2.Vpc.from_lookup(self, 
            'construct_vpc', 
            vpc_id=config['network'].get('vpc_id'),
         
        )

        # you're going to need private subnets not in an array, but cast as an [iSubnet]
        # ``` self.private_iSubnets = self.vpc.private_subnets ``
        # doesn't seem to work like it should. Tthere's something about this version of CDK 
        # that prevents getting subnet groups from the context the way it probably should.
        # Or maybe ist's just the way the VPC sets up using the console wizard.
        # Test later, this shouldn't be here. 
        # See: AUG-12376 after migration to NBCUAS accounts.

        self.private_iSubnets= []
        for idx, subnet_id in enumerate(config['network'].get('private_subnet_ids')):
            self.private_iSubnets.append(
                ec2.Subnet.from_subnet_id(
                    scope=self,
                    id=f"{slug}-{idx}",
                    subnet_id=subnet_id
            )
        )

