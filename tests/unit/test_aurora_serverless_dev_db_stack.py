import aws_cdk as core
import aws_cdk.assertions as assertions

from stacks.db_stack import AuroraServerlessDevDbStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aurora_serverless_dev_db/aurora_serverless_dev_db_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AuroraServerlessDevDbStack(app, "aurora-serverless-dev-db")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
