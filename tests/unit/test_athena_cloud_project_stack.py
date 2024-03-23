import aws_cdk as core
import aws_cdk.assertions as assertions

from athena_cloud_project.athena_cloud_project_stack import AthenaCloudProjectStack

# example tests. To run these tests, uncomment this file along with the example
# resource in athena_cloud_project/athena_cloud_project_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AthenaCloudProjectStack(app, "athena-cloud-project")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
