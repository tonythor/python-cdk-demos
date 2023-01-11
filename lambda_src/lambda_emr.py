import boto3
import requests
import pprint
import datetime
import pprint; 
import json
import os
import logging

#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html 
def send_slack(payload, slack_webhook):
    return requests.post(slack_webhook, json=payload)

def format_slack_msg(title, description, details, is_alert=False):
    color = "#db310f" if is_alert else "#36a64f"    #color is red if alert else green
    more_info = '\n' + description if description else ""
    payload = {'attachments': [{"color": color, "pretext": title, "text": f"```{details}```{more_info}"}]}
    return payload

def format_and_send_slack(title, description, details, is_alert, slack_webhook):
    payload = format_slack_msg(title, description, details, is_alert)
    send_slack(payload, slack_webhook)

def handler(event, context):
    session = boto3.Session()
    emr_client = session.client('emr', region_name= 'us-east-1')
    cw_cli = boto3.client('cloudwatch')
    response = emr_client.list_clusters(ClusterStates=['WAITING'])

    clusters=[]
    for cluster in response.get("Clusters"):
        clusters.append(
            {
            'Id': cluster.get("Id"),
            'Name': cluster.get('Name'),
            'CreationDateTime' : cluster.get("Status").get("Timeline").get("CreationDateTime")
            }
        )
   
    print(clusters)
    if clusters:
        end_time = datetime.datetime.now() 
        start_time = end_time - datetime.timedelta(minutes=15)
        
        for cluster in clusters:
            # print(emr_client.describe_cluster(ClusterId=cluster))
            stats = cw_cli.get_metric_statistics(
                Namespace = 'AWS/ElasticMapReduce',
                MetricName='IsIdle',
                Dimensions=[{'Name': 'JobFlowId','Value': cluster.get("Id")}],
                Statistics=["Average"],
                StartTime=start_time,
                EndTime=end_time,
                Period=60
            )
            data = stats.get("Datapoints")
            # In [29]: data
            # Out[29]:
            # [{'Average': 1.0,'Timestamp': datetime.datetime(2023, 1, 11, 4, 25), 'Unit': 'None'},
            #  {'Average': 1.0,'Timestamp': datetime.datetime(2023, 1, 11, 4, 35), 'Unit': 'None'},
            #  {'Average': 1.0, 'Timestamp': datetime.datetime(2023, 1, 11, 4, 30), 'Unit': 'None'}]
            if data[0].get("Average") == 1 and data[1].get("Average") == 1 and data[2].get("Average") == 1 :
                webhook = "https://hooks.slack.com/services//TEF2GKSV7/BEM8X8HPH/zH3JVwTLoZFW7OZuqaFQy7O3"
                message = f'Cluster: {cluster.get("Id")}/{cluster.get("Name")} created on {cluster.get("CreationDateTime").strftime("%d/%m/%Y:%H:%M:%S")} has been in a both a waiting state (no jobs running), and marked idle for 15 minutes.'
                logging.info(message)
                #format_and_send_slack(title, description, details, is_alert, slack_webhook): 
                format_and_send_slack(title = "Cluster Idle Alert", details = message, is_alert = True, slack_webhook=webhook)

            else:
                pass
    else:
        logging.info("No EMR clusters in waiting state") 


    return {
        'statusCode': 200,
        'body': str(clusters)
    }

# cluster.get("Status").get("StageChangeReason").get("Timeline").get("CreationDateTime")
# {'Cluster': 
#     {
#       'Id': 'j-1YESLJ543HPFC', 
#       'Name': 'HelloAwsAuroraServerless-cdk-generated-demo', 
#       'Status': {
#               'State': 'WAITING', 
#               'StateChangeReason': {
#                     'Message': 
#                     'Cluster ready to run steps.'}, 
#                     'Timeline': {
#                         'CreationDateTime': datetime.datetime(2023, 1, 11, 3, 51, 44, 429000), 
#                         'ReadyDateTime': datetime.datetime(2023, 1, 11, 3, 57, 46, 689000)
#                         }
#                     }, 
#                     'Ec2InstanceAttributes': {
#                         'Ec2SubnetId': 'subnet-010d5bce0313ef1b5', 
#                         'RequestedEc2SubnetIds': ['subnet-010d5bce0313ef1b5'], 
#                         'Ec2AvailabilityZone': 'us-east-1a', 
#                         'RequestedEc2AvailabilityZones': [], 
#                         'IamInstanceProfile': 'emr_job_flow_role', 
#                         'EmrManagedMasterSecurityGroup': 'sg-00f9e3c8f139f30bc', 
#                         'EmrManagedSlaveSecurityGroup': 'sg-0d989c951e6271475', 
#                         'ServiceAccessSecurityGroup': 'sg-0c6a15bc20bc18999', 
#                         'AdditionalMasterSecurityGroups': [], 
#                         'AdditionalSlaveSecurityGroups': []}, 
#                         'InstanceCollectionType': 'INSTANCE_GROUP', 
#                         'LogUri': 's3n://tonyfraser-aws-logging/emr/us-east-1/elasticmapreduce/', 
#                         'ReleaseLabel': 'emr-6.9.0', 
#                         'AutoTerminate': False, 
#                         'TerminationProtected': False, 
#                         'VisibleToAllUsers': True, 
#                         'Applications': [{'Name': 'Spark', 'Version': '3.3.0'}], 
#                         'Tags': [], 
#                         'ServiceRole': 'emrStack-HelloAwsAuroraServerlessclusterrole828780-V1PG0H62PDQD', 
#                         'NormalizedInstanceHours': 0, 
#                         'MasterPublicDnsName': 'ip-10-0-2-121.ec2.internal', 
#                         'Configurations': [{'Classification': 'spark-env', 
#                             'Configurations': [{
#                                 'Classification': 'export', 
#                                 'Properties': {
#                                     'PYSPARK_DRIVER_PYTHON': '/usr/bin/python3', 
#                                     'PYSPARK_PYTHON': '/usr/bin/python3'}
#                              }], 
#                              'Properties': {}},
#                             {'Classification': 'spark-defaults', 'Properties': {'spark.sql.execution.arrow.enabled': 'true'}}, 
#                             {'Classification': 'spark', 'Properties': {'maximizeResourceAllocation': 'true'}}],
#                         'ScaleDownBehavior': 'TERMINATE_AT_TASK_COMPLETION', 
#                         'KerberosAttributes': {}, 
#                         'ClusterArn': 'arn:aws:elasticmapreduce:us-east-1:764573855117:cluster/j-1YESLJ543HPFC', 
#                         'StepConcurrencyLevel': 1, 'PlacementGroups': []}, 
#                         'ResponseMetadata': {'RequestId': '87d1f4c3-15d9-4c58-b983-7e9136cadc09', 'HTTPStatusCode': 200, 
#                         'HTTPHeaders': {'x-amzn-requestid': '87d1f4c3-15d9-4c58-b983-7e9136cadc09', 
#                         'content-type': 'application/x-amz-json-1.1', 'content-length': '1816', 
#                         'date': 'Wed, 11 Jan 2023 04:18:07 GMT'}, 'RetryAttempts': 0}}

# {'Datapoints': 
#     [
#         {'Sum': 1.0,'Timestamp': datetime.datetime(2023, 1, 11, 4, 15),'Unit': 'None'},
#         {'Sum': 1.0,'Timestamp': datetime.datetime(2023, 1, 11, 4, 10),'Unit': 'None'},
#         {'Sum': 1.0,'Timestamp': datetime.datetime(2023, 1, 11, 4, 5), 'Unit': 'None'}
#     ],
#     'Label': 'IsIdle',
#     'ResponseMetadata': {'HTTPHeaders': {'content-length': '742',
#     'content-type': 'text/xml',
#     'date': 'Wed, 11 Jan 2023 04:18:07 GMT',
#     'x-amzn-requestid': 'aa8b0a71-b7b0-4f06-b29f-0365406c888a'},
#     'HTTPStatusCode': 200,
#     'RequestId': 'aa8b0a71-b7b0-4f06-b29f-0365406c888a',
#     'RetryAttempts': 0}}