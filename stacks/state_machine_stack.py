from aws_cdk import (
    Stack,
    CfnOutput,
    Duration,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_ecs as ecs,
    aws_ec2 as ec2)

from constructs import Construct
from stacks.config_nogit import config as config
from stacks.elastic_stack import ElasticContainerServiceStack
from stacks.task_stack import TaskStack
from stacks.network_stack import NetworkStack

class StateMachineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, 
                    elastic_stack:ElasticContainerServiceStack, 
                    task_stack:TaskStack, 
                    network_stack:NetworkStack, **kwargs) -> None:
        slug = config.get('slug')
        super().__init__(scope, construct_id,  stack_name=f"cf{slug}StateMachineStack", **kwargs)

        wait_x = sfn.Wait(self, "Wait X Seconds", time=sfn.WaitTime.duration(Duration.seconds(5)))
        job_failed = sfn.Fail(self, "Job Failed", cause="AWS Batch Job Failed", error="something failed")
        job_succeed = sfn.Succeed(self, "Job passed", comment="Yay")

        launch_strategy = [ecs.PlacementStrategy.packed_by_cpu()]
        launch_constraints = [ecs.PlacementConstraint.distinct_instances()]
        
        task = tasks.EcsRunTask(self, f"{slug}-run-task",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
            cluster=elastic_stack.cluster,
            task_definition=task_stack.task_def,
            subnets= ec2.SubnetSelection(subnets=network_stack.private_iSubnets),
            launch_target=tasks.EcsEc2LaunchTarget(            
                placement_strategies = launch_strategy, 
                placement_constraints= launch_constraints
            )
        )


        chainable_definition = task.next(wait_x) \
            .next(sfn.Choice(self, "Job Complete?") \
                .when(sfn.Condition.string_equals("$.status", "FAILED"), job_failed) \
                .when(sfn.Condition.string_equals("$.status", "SUCCEEDED"), job_succeed) \
            .otherwise(wait_x)
        )

        state_machine = sfn.StateMachine(self, f"{slug}-state-machine",
            definition=chainable_definition,
            timeout=Duration.minutes(5)
        )
        
        CfnOutput(self, id="StateMachineARN",  value=state_machine.state_machine_arn)
        CfnOutput(self, id="StateMachineName", value=state_machine.state_machine_name)
        CfnOutput(self, id="StateMachineType", value=state_machine.state_machine_type.value)


        # now trigger step function with console, or command line like so: 

        # #!/bin/bash
        # slug="slug=HelloAwsAuroraServerlessDevAfraser"
        # STATE_MACHINE=$(aws stepfunctions list-state-machines| jq .stateMachines[].stateMachineArn -r  |grep $slug) 
        # aws stepfunctions start-execution --state-machine-arn $STATE_MACHINE

        # or trigger with event bridge! 

        




