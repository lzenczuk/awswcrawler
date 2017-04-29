import boto3
import time


def get_lambda(function_name):
    lambda_name = function_name_to_lambda_name(function_name)

    client = boto3.client('lambda')
    response = client.list_functions()
    return next((LambdaFunction(lambda_name) for f in response['Functions'] if f['FunctionName'] == lambda_name), None)


def create_lambda(function_name, bucket_name, bucket_key, role_arn):
    client = boto3.client('lambda')

    response = client.create_function(
        FunctionName=function_name_to_lambda_name(function_name),
        Runtime='python2.7',  # 'python3.6'
        Role=role_arn,
        Handler=function_name,
        Code={
            'S3Bucket': bucket_name,
            'S3Key': bucket_key
        },
        Timeout=300,
        MemorySize=256
    )

    return LambdaFunction(function_name)


def delete_lambda(function_name):
    f = get_lambda(function_name)
    if f is None:
        return

    client = boto3.client('lambda')

    client.delete_function(
        FunctionName=function_name_to_lambda_name(function_name)
    )


def function_name_to_lambda_name(function_name):
    return "-".join(function_name.split("."))


class LambdaFunction:
    def __init__(self, function_name):
        self.client = boto3.client('lambda')
        self.function_name = function_name
        self.lambda_name = function_name_to_lambda_name(function_name)

    def add_api_gateway_permission(self, api_id, region=None, account_id=None):
        if region is None:
            region = boto3.session.Session().region_name

        if account_id is None:
            account_id = boto3.client('sts').get_caller_identity().get('Account')

        source_arn = "arn:aws:execute-api:"+region+":"+account_id+":" + api_id + "/*/*"

        statement_id = self.function_name+str(int(time.time()))

        response = self.client.add_permission(
            FunctionName=self.lambda_name,
            StatementId=statement_id,
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=source_arn,
        )

        return response['Statement']

    def get_arn(self):
        return next((f['FunctionArn'] for f in self.client.list_functions()['Functions'] if f['FunctionName'] == self.lambda_name), None)

