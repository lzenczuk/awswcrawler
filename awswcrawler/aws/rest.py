import json

import boto3

from aws.path import parse_request_string
from aws.path import request_params_to_aws_request_params
from aws.path import request_params_to_aws_request_template_dict


def get_api_id(name):
    response = boto3.client('apigateway').get_rest_apis()

    api_id = None
    for i in response['items']:
        if i['name'] == name:
            api_id = i['id']

    return api_id


def delete_rest_api(name):
    api_id = get_api_id(name)
    if api_id is not None:
        boto3.client('apigateway').delete_rest_api(restApiId=api_id)


class Rest:
    """
    Class responsible for creating api gateway endpoints. Example usage:
    
    lb = get_lambda("test_lambda")
    
    api = Rest("test")
    api.map_lambda("GET", "api/users/{user_id}", lb)
    api.map_lambda("POST", "api/users/{user_id}", lb)
    api.map_lambda("GET", "api/users/{user_id}/tasks", lb)
    api.map_lambda("POST", "api/users/{user_id}/tasks?start_id={!start_id}&end_id={!end_id}", lb)
    api.deploy("dev")
    
    """
    def __init__(self, name):
        self.name = name
        self.resources = []
        self.client = boto3.client('apigateway')

        api_id = get_api_id(name)

        if api_id is None:
            response = self.client.create_rest_api(
                name=self.name
            )
            self.api_id = response['id']
        else:
            self.api_id = api_id

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

    def is_path_exists(self, path):
        return self.get_path_id(path) is not None

    def get_root_path_id(self):
        return self.get_path_id("/")

    def create_resource(self, path, parent_id):
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

    def map_lambda(self, method, path, lambda_function):
        request_params = parse_request_string(path)

        aws_request_params = request_params_to_aws_request_params(request_params)
        aws_request_template_dict = request_params_to_aws_request_template_dict(request_params)

        resources_array = list(r['request_string'] for r in request_params if r['type'] == "PATH" or r['type'] == "PATH_PARAM")

        parent_id = self.create_path(resources_array)

        self.__map_lambda(parent_id, method, aws_request_params, aws_request_template_dict, lambda_function)

    def create_path(self, resources_array):
        return self.__recursion_create_path_id("", resources_array, self.get_root_path_id())

    def __recursion_create_path_id(self, path_string, resources_array, parent_id):
        if not resources_array:
            return parent_id

        path_string = path_string+"/"+resources_array[0]
        if self.is_path_exists(path_string):
            return self.__recursion_create_path_id(path_string, resources_array[1:], self.get_path_id(path_string))
        else:
            return self.__recursion_create_path_id(path_string, resources_array[1:], self.create_resource(resources_array[0], parent_id))

    def __map_lambda(self, parent_id, method, request_params, request_template_dict, lb):

        self.client.put_method(
            restApiId=self.api_id,
            resourceId=parent_id,
            httpMethod=method,
            authorizationType='NONE',
            requestParameters=request_params,
        )

        self.client.put_method_response(
            restApiId=self.api_id,
            resourceId=parent_id,
            httpMethod=method,
            statusCode='200'
        )

        self.client.put_integration(
            restApiId=self.api_id,
            resourceId=parent_id,
            httpMethod=method,
            type='AWS',
            integrationHttpMethod='POST',
            uri="arn:aws:apigateway:" + boto3.session.Session().region_name + ":lambda:path/2015-03-31/functions/" + lb.get_arn() + "/invocations",
            passthroughBehavior='WHEN_NO_MATCH',
            requestTemplates={
                "application/json": json.dumps(request_template_dict)
            }
        )

        self.client.put_integration_response(
            restApiId=self.api_id,
            resourceId=parent_id,
            httpMethod=method,
            statusCode='200',
            selectionPattern=''  # Fix Invalid request input bug >:(
        )

        account_id = boto3.client('sts').get_caller_identity().get('Account')
        lb.add_api_gateway_permission(self.api_id, account_id=account_id)

