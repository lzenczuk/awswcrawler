import boto3
import time
from botocore.exceptions import ClientError


def get_lambda(function_name):
    lambda_name = function_name_to_lambda_name(function_name)

    client = boto3.client('lambda')
    response = client.list_functions()
    return next((LambdaFunction(lambda_name) for f in response['Functions'] if f['FunctionName'] == lambda_name), None)


# instead of providing function name provide function. Generate name using
# f.__module__+"."+f.__name__
def create_lambda(function_name, bucket_name, bucket_key, role_arn):
    client = boto3.client('lambda')

    try:
        __create_lambda__(bucket_key, bucket_name, client, function_name, role_arn)
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidParameterValueException':
            print("Error creating lambda. Possible problem with role replication. Waiting 10s to retry...")
            time.sleep(10)
            __create_lambda__(bucket_key, bucket_name, client, function_name, role_arn)
            return
        else:
            raise e

    return LambdaFunction(function_name)


def __create_lambda__(bucket_key, bucket_name, client, function_name, role_arn):
    client.create_function(
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

        statement_id = self.function_name.replace(".", "-")+"-"+str(int(time.time()))

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


