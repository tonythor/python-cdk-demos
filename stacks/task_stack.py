from operator import sub

from aws_cdk import (
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_iam as iam,
    aws_logs as logs,
    aws_ecs as ecs)
from constructs import Construct
from stacks.config import config as config

class TaskStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,  **kwargs) -> None:
        slug = config.get('slug')
        super().__init__(scope, construct_id,  stack_name=f"cf{slug}TaskStack", **kwargs)

        execution_role = iam.Role(self, f"{slug}my-ecs-task-role", 
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            role_name="run_my_task")
        execution_role.add_managed_policy( 
                iam.ManagedPolicy.from_managed_policy_arn(
                    self, 'containerRole','arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy'
        ))

        log_group = logs.LogGroup(self, f"/ecs/{slug}", 
            log_group_name=f"/ecs/{slug}",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY)

        self.task_def =  ecs.TaskDefinition(self, 
            id=f"{slug}-task-def",
            execution_role=execution_role,
            family=config['ecs'].get('family'),
            network_mode=ecs.NetworkMode.AWS_VPC,
            compatibility=ecs.Compatibility.EC2,
        
        )

        self.task_def.add_container(f"{slug}-add-container", 
            logging=ecs.LogDrivers.aws_logs(log_group=log_group, stream_prefix=config.get('slug')),
            command=config['ecs'].get('command'),
            essential=True,
            memory_limit_mib=256,
            environment={'DB_SECRET_LOCATION':'COFFEE'},
            image=ecs.ContainerImage.from_registry(config['ecs'].get('image')))
        

        CfnOutput(self, id="ExecutionRole Name", value=execution_role.role_name)
        CfnOutput(self, id="ExecutionRole Arn", value=execution_role.role_arn)
        CfnOutput(self, id="TaskDef Arn", value=self.task_def.task_definition_arn)