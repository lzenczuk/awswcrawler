import boto3
import json
import logging


class StackTemplate:

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.resources = {}
        self.client = boto3.client('cloudformation')

    def add_resource(self, resource_name, resource):
        """
        :param resource_name: (A-Za-z0-9) 
        :param resource: 
        :return: 
        """
        self.resources[resource_name] = resource
        return resource

    def cf_resource(self):
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Resources": {}
        }

        for resource_name, resource in self.resources.items():
            template['Resources'][resource_name] = resource.cf_resource()

        return template

    def deploy(self, stack_name):
        json_template = json.dumps(self.cf_resource())

        self.logger.info("Deploying stack %s" % stack_name)
        self.logger.debug("Stack %s template: %s" % (stack_name, json_template))

        response = self.client.create_stack(
            StackName=stack_name,
            TemplateBody=json_template
        )

        stack_id = response['StackId']
        self.logger.info("Stack %s received id %s" % (stack_name, stack_id))

        return stack_id

