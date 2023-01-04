from operator import sub
from re import L

from aws_cdk import (
    Stack,
    aws_emr as emr,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling)
from constructs import Construct

from stacks.config_nogit import config as config
from stacks.network_stack import NetworkStack


class EMRStack(Stack):
    def __init__( self, scope: Construct, id: str, network_stack, **kwargs) -> None:
        slug = config.get('slug')
        super().__init__(scope, id, **kwargs)

        s3_script_bucket = config['emr'].get('s3_script_bucket')
        spark_script = config['emr'].get('spark_script')
        s3_log_bucket = config['emr'].get('s3_log_bucket')

        read_scripts_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:GetObject",],
            resources=[f"arn:aws:s3:::{s3_script_bucket}/*"],
        )

        read_scripts_document = iam.PolicyDocument()
        read_scripts_document.add_statements(read_scripts_policy)

        master_sg = ec2.SecurityGroup(self, id=f"{config.get('slug')}master", vpc = network_stack.vpc, allow_all_outbound=True, description=f"{config.get('slug')}")
        master_sg.add_ingress_rule(ec2.Peer.ipv4(config['network'].get('sn1_cider')), ec2.Port.all_tcp())
        master_sg.add_ingress_rule(ec2.Peer.ipv4(config['network'].get('sn2_cider')), ec2.Port.all_tcp())
        # master_sg.add_ingress_rule(ec2.Peer.ipv4(config['network'].get('sn1_cider')), ec2.Port.all_udp())
        # master_sg.add_ingress_rule(ec2.Peer.ipv4(config['network'].get('sn2_cider')), ec2.Port.all_udp())
        
        slave_sg = ec2.SecurityGroup(self, id=f"{config.get('slug')}slave", vpc = network_stack.vpc, allow_all_outbound=True, description=f"{config.get('slug')}")
        slave_sg.add_ingress_rule(ec2.Peer.ipv4(config['network'].get('sn1_cider')), ec2.Port.all_tcp())
        slave_sg.add_ingress_rule(ec2.Peer.ipv4(config['network'].get('sn2_cider')), ec2.Port.all_tcp())
        # slave_sg.add_ingress_rule(ec2.Peer.ipv4(config['network'].get('sn1_cider')), ec2.Port.all_udp())
        # slave_sg.add_ingress_rule(ec2.Peer.ipv4(config['network'].get('sn2_cider')), ec2.Port.all_udp())

        service_sg = ec2.SecurityGroup(self, id=f"{config.get('slug')}service", vpc = network_stack.vpc, allow_all_outbound=True, description=f"{config.get('slug')}")
        service_sg.add_ingress_rule(ec2.Peer.ipv4(config['network'].get('sn1_cider')), ec2.Port.all_tcp())
        service_sg.add_ingress_rule(ec2.Peer.ipv4(config['network'].get('sn2_cider')), ec2.Port.all_tcp())
        # service_sg.add_ingress_rule(ec2.Peer.ipv4(config['network'].get('sn1_cider')), ec2.Port.all_udp())
        # service_sg.add_ingress_rule(ec2.Peer.ipv4(config['network'].get('sn2_cider')), ec2.Port.all_udp())
        service_sg.connections.allow_from(master_sg, ec2.Port.tcp(9443), 'master_sg')
        # ec2SecurityGroup.connections.allowFrom(elbSecurityGroup, Port.tcp(443), 'Application Load Balancer')

        # emr service role
        cluster_role = iam.Role(
            self,
            "cluster_role",
            assumed_by=iam.ServicePrincipal("elasticmapreduce.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonElasticMapReduceRole")
              ],
            inline_policies={
                "read_scripts_document": read_scripts_document
            }
        )

        # ])

        # emr job flow role
        emr_job_flow_role = iam.Role(
            self,
            "emr_job_flow_role",
            role_name = "emr_job_flow_role",
            description="emr job flow role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonElasticMapReduceforEC2Role"),    
            ],
        )

        emr_job_flow_role.add_managed_policy(iam.ManagedPolicy.from_managed_policy_arn(
            self, 'CloudWatchAgentServerPolicy','arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy'))

        emr_job_flow_role.add_managed_policy(iam.ManagedPolicy.from_managed_policy_arn(
            self, 'AmazonSSMManagedInstanceCore','arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'))

        emr_job_flow_role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:*"],
                resources=["*"]))
        
       
        # emr job flow profile
        emr_job_flow_profile = iam.CfnInstanceProfile(
            self,
            "emr_job_flow_profile",
            instance_profile_name="emr_job_flow_role",
            roles=["emr_job_flow_role"]
        )


        assert emr_job_flow_profile.instance_profile_name is not None

        # create emr cluster
        emr.CfnCluster(
            self,
            "emr_cluster",
            instances=emr.CfnCluster.JobFlowInstancesConfigProperty(
                core_instance_group=emr.CfnCluster.InstanceGroupConfigProperty(
                    instance_count=1,
                    instance_type="m4.large"
                ),
                ec2_subnet_id='subnet-001fff36cd9f05ca4',
                service_access_security_group=service_sg.security_group_id,
                emr_managed_master_security_group=master_sg.security_group_id,
                emr_managed_slave_security_group=slave_sg.security_group_id,
                hadoop_version="Amazon",
                keep_job_flow_alive_when_no_steps=True,  #<-- Leave it running
                master_instance_group=emr.CfnCluster.InstanceGroupConfigProperty(
                    instance_count=1, instance_type="m4.large"
                ),
            ),
            # note job_flow_role is an instance profile (not an iam role)
            job_flow_role=emr_job_flow_profile.instance_profile_name,
            name=f"{slug}-cdk-generated-demo",
            applications=[emr.CfnCluster.ApplicationProperty(name="Spark")],
            service_role=cluster_role.role_name,
            bootstrap_actions= [emr.CfnCluster.BootstrapActionConfigProperty(
                name="name",
                script_bootstrap_action=emr.CfnCluster.ScriptBootstrapActionConfigProperty(
                        path="s3://tonyfraser-admin/cloudwatch-agent/config_emr.sh"
                    )
            )],
            configurations=[
                # use python3 for pyspark
                emr.CfnCluster.ConfigurationProperty(
                    classification="spark-env",
                    configurations=[
                        emr.CfnCluster.ConfigurationProperty(
                            classification="export",
                            configuration_properties={
                                "PYSPARK_PYTHON": "/usr/bin/python3",
                                "PYSPARK_DRIVER_PYTHON": "/usr/bin/python3",
                            },
                        )
                    ],
                ),
                # enable apache arrow
                emr.CfnCluster.ConfigurationProperty(
                    classification="spark-defaults",
                    configuration_properties={
                        "spark.sql.execution.arrow.enabled": "true"
                    },
                ),
                # dedicate cluster to single jobs
                emr.CfnCluster.ConfigurationProperty(
                    classification="spark",
                    configuration_properties={"maximizeResourceAllocation": "true"},
                )
            ],
            log_uri=f"s3://tonyfraser-aws-logging/emr/us-east-1/elasticmapreduce/",
            release_label="emr-6.9.0",
            visible_to_all_users=False,
        )
            # This is how you send a job.
            # steps=[
            #     emr.CfnCluster.StepConfigProperty(
            #         hadoop_jar_step=emr.CfnCluster.HadoopJarStepConfigProperty(
            #             jar="command-runner.jar",
            #             args=[
            #                 "spark-submit",
            #                 "--deploy-mode",
            #                 "cluster",
            #                 f"s3://{s3_script_bucket}/scripts/{spark_script}",
            #             ],
            #         ),
            #         name="step_name",
            #         action_on_failure="CONTINUE",
            #     ),
            # ],
       

