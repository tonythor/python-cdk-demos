from aws_cdk import (
    Duration, Stack, CfnOutput,
    aws_rds as rds,
    aws_ec2 as ec2 
)

from constructs import Construct
from stacks.config import config

class DBStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, network_stack, **kwargs) -> None:
        slug = config.get('slug')
       
        super().__init__(scope, construct_id,  stack_name=f"{slug}DbStack", **kwargs)

        self.sg:ec2.SecurityGroup = ec2.SecurityGroup(self, id=f"{slug}SG", vpc = network_stack.vpc, allow_all_outbound=True, description=f"{slug}")
        self.sg.add_ingress_rule(ec2.Peer.ipv4(config['network'].get('sn1_cider')), ec2.Port.all_tcp())
        self.sg.add_ingress_rule(ec2.Peer.ipv4(config['network'].get('sn2_cider')), ec2.Port.all_tcp())

        # don't do this anyIpv4 thing like below.
        # self.sg.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(22), 'SSH frm anywhere');    
        
        self.aurora:rds.ServerlessCluster = rds.ServerlessCluster(self, id=f"{slug}", 
            cluster_identifier=config.get("slug"),
            default_database_name=config['db'].get('default_database_name'),
            scaling= rds.ServerlessScalingOptions(
                        auto_pause=Duration.minutes(5),             # default is to pause after 5 minutes of idle time
                        min_capacity=rds.AuroraCapacityUnit.ACU_2,  # default is 2 Aurora capacity units (ACUs)
                        max_capacity=rds.AuroraCapacityUnit.ACU_16), 
            engine=rds.DatabaseClusterEngine.AURORA_POSTGRESQL,
            parameter_group=rds.ParameterGroup.from_parameter_group_name(self, "ParameterGroup", "default.aurora-postgresql10"),
            enable_data_api=True,
            vpc=network_stack.vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=network_stack.private_iSubnets),
            security_groups=[self.sg]
            )


        secret_arn = self.aurora.secret.secret_arn
        secret_name = self.aurora.secret.secret_name
        url = f"{str(self.aurora.cluster_endpoint.hostname)}:{str(self.aurora.cluster_endpoint.port)}"
    
        CfnOutput(self, id="rds-db-url host", value=url)
        CfnOutput(self, id="secret_arn", value=secret_arn)
        CfnOutput(self, id="secret_name", value=secret_name)


