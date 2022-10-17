from operator import sub
from re import L

from aws_cdk import (
    Stack,
    CfnOutput,
    aws_iam as iam,
    aws_ec2 as ec2, 
    aws_ecs as ecs,
    aws_autoscaling as autoscaling)
from constructs import Construct
from stacks.config import config as config
from stacks.network_stack import NetworkStack


class ElasticContainerServiceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, network_stack, **kwargs) -> None:
        slug = config.get('slug')
        super().__init__(scope, construct_id,  stack_name=f"{slug}ElasticStack", **kwargs)
 
        ecs_role = iam.Role(self, f"{slug}-ecsRole", 
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            role_name=f'{config.get("slug")}-ecs-role')
            
        ecs_role.add_managed_policy( 
                iam.ManagedPolicy.from_managed_policy_arn(
                    self, 'containerService', 'arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role'
            ))

        ecs_role.add_managed_policy( 
                iam.ManagedPolicy.from_managed_policy_arn(
                    self, 'containerPermissions','arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy'
            ))

        ecs_role.add_managed_policy( 
                iam.ManagedPolicy.from_managed_policy_arn(
                    self, 'stepFunctionPermission','arn:aws:iam::aws:policy/AWSStepFunctionsFullAccess'
            ))

        self.cluster = ecs.Cluster(self, f"{slug}-cluster", vpc=network_stack.vpc)

        launch_template = ec2.LaunchTemplate(self, f"{slug}-launch_template",
            role=ecs_role,
            instance_type=ec2.InstanceType('t3.medium'),
            machine_image=ecs.EcsOptimizedImage.amazon_linux(),
            user_data=ec2.UserData.for_linux()
        )

        ## todo -> AUG12357 - When this goes to a permanent account, make sure the ASG cdk destroys
        auto_scaling_group = autoscaling.AutoScalingGroup(self, f"{slug}-asg",
            vpc=network_stack.vpc,
            max_capacity=2,
            min_capacity=1,
            launch_template=launch_template,
            termination_policies=[autoscaling.TerminationPolicy.DEFAULT],
            # Below is from ```bash: cdk context ``` 
            #  ... "subnetGroups": [ { 
            #   "name": "Isolated", 
            #   "type": "Isolated", 
            #   "subnets": { ...
            # vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED) 
            # but that's not an option.
            #
            # So this would follow.... 
            # class SubnetTypeTwo(ec2.SubnetType):
            #     PRIVATE = "PRIVATE"
            #     ISOLATED = "ISOLATED"
            #     DEPRECATED_ISOLATED = "DEPRECATED_ISOLATED"
            # vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)  
            # CDK doesn't seem to like it though, so just hard code the subnets into config.py.
            # 
            # todo -> Test subnet_type instead of subnets on whatever network this ends up on.
            # See: AUG-12376
            vpc_subnets=ec2.SubnetSelection(subnets=network_stack.private_iSubnets)
        )

        capacity_provider = ecs.AsgCapacityProvider(self, 
            id=f"{slug}cap-provider",
            auto_scaling_group=auto_scaling_group,
            machine_image_type=ecs.MachineImageType.AMAZON_LINUX_2
        )
        self.cluster.add_asg_capacity_provider(capacity_provider)
 
        CfnOutput(self, id="cluster_name", value=self.cluster.cluster_name)
