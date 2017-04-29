import boto3
import pprint
import json

client = boto3.client('apigateway')

pp = pprint.PrettyPrinter()

api_id = 'hffqnh47fc'
resource_id = 'lapquo'

response = client.get_rest_api(
    restApiId=api_id
)

print("-----------> api")
pp.pprint(response)

response = client.get_resources(
    restApiId=api_id
)

print("-----------> resources")
pp.pprint(response)

response = client.get_method(
    restApiId=api_id,
    resourceId=resource_id,
    httpMethod='GET'
)

print("-----------> method")
print(json.dumps(response))

response = client.get_deployments(
    restApiId=api_id,
)

print("-----------> deployments")
pp.pprint(response)


