from operator import sub
from aws_cdk import (
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_iam as iam,
    aws_logs as logs,
    aws_ecr as ecr,
    aws_ec2 as ec2,
    aws_ecr_assets as assets)
from cdk_ecr_deployment import (
    ECRDeployment as ecr_deploy,
    DockerImageName as docker_image_name)
from stacks.config_nogit import config as config


from constructs import Construct
from pathlib import Path

from stacks.network_stack import NetworkStack

class DockerImageStack(Stack):
    """
    This stack creates a docker image from the code within the ./docker_src directory. Take full docker url
    and put it in config.py. (This could be linked, let's not do that.) 

    To use, make sure you have your local docker daemon running.
    
    """

    def __init__(self, scope: Construct, construct_id: str, network_stack:NetworkStack, **kwargs) -> None:
        slug = config.get('slug')
        super().__init__(scope, construct_id,  stack_name=f"{slug}DockerImageStack", **kwargs)
    

        ## you might have to go manually create a repository for CDK to work with
        ## seems to be the case for me now. cdk-hnb659fds-container-assets-764573855117-us-east-1 
        #     [100%] fail: No ECR repository named 'cdk-hnb659fds-container-assets-764573855117-us-east-1' in account 764573855117. Is this account bootstrapped?
        #  ❌ Building assets failed: Error: Building Assets Failed: Error: Failed to build one or more assets. See the error messages above for more information.
        #     at buildAllStackAssets (/Users/afraser/.nvm/versions/node/v18.3.0/lib/node_modules/aws-cdk/lib/build.ts:21:11)
        #     at processTicksAndRejections (node:internal/process/task_queues:95:5)
        #     at CdkToolkit.deploy (/Users/afraser/.nvm/versions/node/v18.3.0/lib/node_modules/aws-cdk/lib/cdk-toolkit.ts:175:7)
        #     at initCommandLine (/Users/afraser/.nvm/versions/node/v18.3.0/lib/node_modules/aws-cdk/lib/cli.ts:357:12)


        actions=[
            "ecr:BatchCheckLayerAvailability",
            "ecr:CreateRepository",
            "ecr:BatchGetImage",
            "ecr:CompleteLayerUpload",
            "ecr:DescribeImageScanFindings",
            "ecr:DescribeImages",
            "ecr:DescribeRepositories",
            "ecr:GetAuthorizationToken",
            "ecr:GetDownloadUrlForLayer",
            "ecr:GetRepositoryPolicy",
            "ecr:InitiateLayerUpload",
            "ecr:ListImages",
            "ecr:ListTagsForResource",
            "ecr:PutImage",
            "ecr:UploadLayerPart",
            "s3:GetObject"
        ]

        statement = iam.PolicyStatement(actions=actions,resources=["*"])
        policy_document =  iam.PolicyDocument(statements=[statement])
        managed_policy = iam.ManagedPolicy(self, document=policy_document, id=f"{slug}-policy")

        cdk_deploy_role = iam.Role(self, id=f"{slug}-cdk-deploy-role",
            managed_policies=[managed_policy],
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="a role created from the codebase of gitlab:hello-aws"
        )

        repository:ecr.Repository = ecr.Repository(self, 
            id=f"{slug}",
            removal_policy=RemovalPolicy.DESTROY
        )


        docker:assets.DockerImageAsset = assets.DockerImageAsset(self, 
            "MyBuildImage",
            directory="docker_src"
        )
        

        ecr_deploy(self, 'DeployDockerImage', 
            role=cdk_deploy_role,
            src=docker_image_name(docker.image_uri), 
            dest=docker_image_name(f"{repository.repository_uri}:latest")
        )


