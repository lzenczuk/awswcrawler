import boto3

from aws.lambdas import get_lambda

region = "eu-west-1"

lb = get_lambda("awswcrawler.lambdas.batch_download.lambdas.create_batch_endpoint")
if lb is None:
    raise ValueError("No lambda")

lambda_arn = lb.get_arn()

client = boto3.client('apigateway')

response = client.create_rest_api(
    name="test_api1"
)
print("---> create api: "+str(response))
api_id = response['id']

response = client.get_resources(
    restApiId=api_id
)
print("---> get resources: "+str(response))

root_resource_id = next((r['id'] for r in response['items'] if r['path'] == "/"), None)
if root_resource_id is None:
    raise ValueError("No root id")

response = client.create_resource(
    restApiId=api_id,
    parentId=root_resource_id,
    pathPart="downloads"
)
print("---> create resource: "+str(response))

downloads_resource_id = response['id']

## Request parameters
# method.request.querystring.{name}
# method.request.path.{name}
# method.request.header.{name}
response = client.put_method(
    restApiId=api_id,
    resourceId=downloads_resource_id,
    httpMethod='GET',
    authorizationType='NONE',
    requestParameters={
        'method.request.querystring.start_id': True,
        'method.request.querystring.end_id': True
    },
)
print("---> create method: "+str(response))

response = client.put_method_response(
    restApiId=api_id,
    resourceId=downloads_resource_id,
    httpMethod='GET',
    statusCode='200'
)
print("---> create method response: "+str(response))

response = client.put_integration(
    restApiId=api_id,
    resourceId=downloads_resource_id,
    httpMethod='GET',
    type='AWS',
    integrationHttpMethod='POST',
    uri="arn:aws:apigateway:"+region+":lambda:path/2015-03-31/functions/"+lambda_arn+"/invocations",
    passthroughBehavior='WHEN_NO_MATCH'
)
print("---> create integration: "+str(response))

response = client.put_integration_response(
    restApiId=api_id,
    resourceId=downloads_resource_id,
    httpMethod='GET',
    statusCode='200',
    selectionPattern='' # Fix Invalid request input bug >:(
)
print("---> create integration response: "+str(response))

response = client.get_resources(
    restApiId=api_id
)
print("---> get resources: "+str(response))

response = client.create_deployment(
    restApiId=api_id,
    stageName='dev'
)
print("---> create deployment: "+str(response))
deployment_id = response['id']

account_id = boto3.client('sts').get_caller_identity().get('Account')

lb.add_api_gateway_permission(api_id, account_id=account_id)



"""client.delete_rest_api(
    restApiId=api_id
)"""

