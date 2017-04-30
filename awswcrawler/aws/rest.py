import boto3
import json

from aws.lambdas import get_lambda


class Rest:
    def __init__(self, name):
        self.name = name
        self.resources = []
        self.client = boto3.client('apigateway')

        response = self.client.create_rest_api(
            name=self.name
        )
        self.api_id = response['id']

        response = self.client.get_resources(
            restApiId=self.api_id
        )

        self.root_resource_id = next((r['id'] for r in response['items'] if r['path'] == "/"), None)
        if self.root_resource_id is None:
            raise ValueError("No root id")

    def get_path_id(self, path):
        response = self.client.get_resources(
            restApiId=self.api_id
        )

        return next((r['id'] for r in response['items'] if r['path'] == path), None)

    def create_path(self, path, parent_id):
        response = self.client.create_resource(
            restApiId=self.api_id,
            parentId=parent_id,
            pathPart=path
        )
        return response['id']

    def deploy(self, stage_name):
        response = self.client.create_deployment(
            restApiId=self.api_id,
            stageName=stage_name
        )
        return response['id']


class Resource:
    def __init__(self, path):
        if path.startswith('/'):
            path = path[1:]

        if path.endswith('/'):
            path = path[:-1]

        self.__path = path
        self.__method = 'GET'
        self.__query_string_params = []
        self.__path_params = []
        self.__header_params = []
        self.__lambda_function = None

        self.__client = None

    def GET(self):
        self.__method = 'GET'
        return self

    def POST(self):
        self.__method = 'POST'
        return self

    def PUT(self):
        self.__method = 'PUT'
        return self

    def DELETE(self):
        self.__method = 'DELETE'
        return self

    def with_querystring_param(self, name, required=True):
        self.__query_string_params.append({'name': name, 'required': required})
        return self

    def calling_lambda(self, lambda_function):
        self.__lambda_function = lambda_function
        return self

    def add_to_api(self, api):
        if self.__lambda_function is None:
            raise ValueError("Missing lambda function")

        request_params = {}
        request_template_dict = {}

        for qsp in self.__query_string_params:
            request_params['method.request.querystring.' + qsp['name']] = qsp['required']
            request_template_dict[qsp['name']] = "$input.params('%s')" % qsp['name']

        resources = self.__path.split("/")

        tmp_path = ""
        parent_id = api.get_path_id("/")

        for r_path in resources:
            tmp_path = tmp_path + '/' + r_path
            tmp_parent_id = api.get_path_id(tmp_path)

            if tmp_parent_id is None:
                parent_id = api.create_path(r_path, parent_id)
            else:
                parent_id = tmp_parent_id

        if self.__client is None:
            self.__client = boto3.client('apigateway')

        self.__client.put_method(
            restApiId=api.api_id,
            resourceId=parent_id,
            httpMethod=self.__method,
            authorizationType='NONE',
            requestParameters=request_params,
        )

        self.__client.put_method_response(
            restApiId=api.api_id,
            resourceId=parent_id,
            httpMethod=self.__method,
            statusCode='200'
        )

        self.__client.put_integration(
            restApiId=api.api_id,
            resourceId=parent_id,
            httpMethod=self.__method,
            type='AWS',
            integrationHttpMethod='POST',
            uri="arn:aws:apigateway:" + boto3.session.Session().region_name + ":lambda:path/2015-03-31/functions/" + self.__lambda_function.get_arn() + "/invocations",
            passthroughBehavior='WHEN_NO_MATCH',
            requestTemplates={
                "application/json": json.dumps(request_template_dict)
            }
        )

        self.__client.put_integration_response(
            restApiId=api.api_id,
            resourceId=parent_id,
            httpMethod=self.__method,
            statusCode='200',
            selectionPattern=''  # Fix Invalid request input bug >:(
        )

        account_id = boto3.client('sts').get_caller_identity().get('Account')
        self.__lambda_function.add_api_gateway_permission(api.api_id, account_id=account_id)


lb = get_lambda("awswcrawler.lambdas.batch_download.lambdas.create_batch_endpoint")

api = Rest("test")
Resource("api/download/batch").POST().with_querystring_param("start_id").with_querystring_param(
    "end_id").calling_lambda(lb).add_to_api(api)
Resource("api/download/batch").GET().with_querystring_param("start_id").with_querystring_param("end_id").calling_lambda(
    lb).add_to_api(api)
api.deploy("dev")
