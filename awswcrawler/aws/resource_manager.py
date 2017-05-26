import json

import os
import time

import awswcrawler.aws.s3 as s3
import awswcrawler.aws.ddb as ddb
import awswcrawler.aws.role as role
import awswcrawler.aws.lambdas as lambdas
import awswcrawler.aws.rest as rest
from awswcrawler.aws.rest import Rest
import awswcrawler.aws.sqs as sqs


class LocalFolderResourceCreationLogger:
    def __init__(self, log_folder, log_name):
        if not os.path.exists(log_folder):
            raise RuntimeError("Log folder %s not exists." % log_folder)

        if not os.path.isdir(log_folder):
            raise RuntimeError("Log folder %s is not directory." % log_folder)

        self.log_folder_path = os.path.join(log_folder, log_name)

        if os.path.exists(self.log_folder_path):
            if not os.path.isdir(self.log_folder_path):
                raise RuntimeError("Inner log folder %s is not directory." % self.log_folder_path)
        else:
            os.makedirs(self.log_folder_path)

    def add_resource(self, name, resource_type, **kwargs):
        file_name = "%s_local_log.json" % str(time.time())

        file_path = os.path.join(self.log_folder_path, file_name)

        with open(file_path, "w") as f:
            if kwargs is None:
                entry = {
                    "resource_type": resource_type,
                    "resource_name": name,
                    "extra_params": None
                }
            else:
                entry = {
                    "resource_type": resource_type,
                    "resource_name": name,
                    "extra_params": kwargs
                }

            f.write(json.dumps(entry))

        return file_name

    def get_resource_logs(self):
        files = [f for f in os.listdir(self.log_folder_path) if os.path.isfile(os.path.join(self.log_folder_path, f))]
        files.sort()
        files.reverse()

        resources = []

        for file_name in files:

            file_path = os.path.join(self.log_folder_path, file_name)

            with open(file_path, "r") as f:
                entry = json.loads(f.read())

                resource = {
                    "resource_id": file_name,
                    "resource_name": entry['resource_name'],
                    "resource_type": entry['resource_type']
                }

                if 'extra_params' in entry:
                    resource['extra_params'] = entry['extra_params']

                resources.append(resource)

        return resources

    def find_resource_log(self, name, resource_type):
        files = [f for f in os.listdir(self.log_folder_path) if os.path.isfile(os.path.join(self.log_folder_path, f))]
        files.sort()
        files.reverse()

        for file_name in files:

            file_path = os.path.join(self.log_folder_path, file_name)

            with open(file_path, "r") as f:
                entry = json.loads(f.read())
                if entry['resource_name'] == name and entry['resource_type'] == resource_type:

                    resource = {
                        "resource_id": file_name,
                        "resource_name": entry['resource_name'],
                        "resource_type": entry['resource_type']
                    }

                    if 'extra_params' in entry:
                        resource['extra_params'] = entry['extra_params']

                    return resource

        return None

    def delete_resource_log(self, resource_id):
        os.remove(os.path.join(self.log_folder_path, resource_id))

    def destroy(self):
        files = [f for f in os.listdir(self.log_folder_path) if os.path.isfile(os.path.join(self.log_folder_path, f))]

        if len(files) != 0:
            raise RuntimeError("Can not destroy local folder resource creation logger. Not all resources destroyed.")

        os.removedirs(self.log_folder_path)


class ResourceManager:
    def __init__(self, resource_creation_logger):
        self.resource_creation_logger = resource_creation_logger

    def create_bucket(self, name, acl='private'):
        bucket = s3.create_bucket(name, acl)
        self.resource_creation_logger.add_resource(name, "s3_bucket")

        return bucket

    def destroy_bucket(self, name):
        resource = self.resource_creation_logger.find_resource_log(name, "s3_bucket")

        if resource is not None:
            s3.delete_bucket(name)

        self.resource_creation_logger.delete_resource_log(resource['resource_id'])

    def create_ddb_table(self, name, pk_name, pk_type, sk_name=None, sk_type=None, read_capacity=5, write_capacity=5):
        table = ddb.create_table_with_pk_and_sk(name, pk_name, pk_type, sk_name, sk_type, read_capacity, write_capacity)
        self.resource_creation_logger.add_resource(name, "ddb_table")

        return table

    def destroy_ddb_table(self, name):
        resource = self.resource_creation_logger.find_resource_log(name, "ddb_table")

        if resource is not None:
            ddb.delete_table(name)

        self.resource_creation_logger.delete_resource_log(resource['resource_id'])

    def create_lambda_role(self, name):
        lambda_role = role.create_role(name)
        self.resource_creation_logger.add_resource(name, "lambda_role")

        return lambda_role

    def destroy_lambda_role(self, name):
        resource = self.resource_creation_logger.find_resource_log(name, "lambda_role")

        if resource is not None:
            role.delete_role(name)

        self.resource_creation_logger.delete_resource_log(resource['resource_id'])

    def create_lambda(self, lambda_function_name, bucket_name, bucket_key, role_arn):
        lambda_function = lambdas.create_lambda(lambda_function_name, bucket_name, bucket_key, role_arn)
        self.resource_creation_logger.add_resource(lambda_function_name, "lambda_function")

        return lambda_function

    def destroy_lambda(self, name):
        resource = self.resource_creation_logger.find_resource_log(name, "lambda_function")

        if resource is not None:
            lambdas.delete_lambda(name)

        self.resource_creation_logger.delete_resource_log(resource['resource_id'])

    def create_rest_api(self, rest_api_name):
        rest_api = Rest(rest_api_name)
        self.resource_creation_logger.add_resource(rest_api_name, "rest_api")

        return rest_api

    def destroy_rest_api(self, name):
        resource = self.resource_creation_logger.find_resource_log(name, "rest_api")

        if resource is not None:
            rest.delete_rest_api(name)

        self.resource_creation_logger.delete_resource_log(resource['resource_id'])

    def create_standard_sqs_queue(self, name):
        queue = sqs.create_standard_sqs_queue(name)
        self.resource_creation_logger.add_resource(name, "sqs", queue_url=queue.queue_url)

        return queue

    def destroy_sqs(self, name):
        resource = self.resource_creation_logger.find_resource_log(name, "sqs")

        if resource is not None:
            sqs.delete_sqs_queue(resource['extra_params']['queue_url'])

        self.resource_creation_logger.delete_resource_log(resource['resource_id'])

    def destroy(self):
        rl = self.resource_creation_logger.get_resource_logs()

        for resource in rl:
            if resource['resource_type'] == "s3_bucket":
                self.destroy_bucket(resource['resource_name'])
            elif resource['resource_type'] == "ddb_table":
                self.destroy_ddb_table(resource['resource_name'])
            elif resource['resource_type'] == "lambda_role":
                self.destroy_lambda_role(resource['resource_name'])
            elif resource['resource_type'] == "lambda_function":
                self.destroy_lambda(resource['resource_name'])
            elif resource['resource_type'] == "rest_api":
                self.destroy_rest_api(resource['resource_name'])
            elif resource['resource_type'] == "sqs":
                self.destroy_sqs(resource['resource_name'])
            else:
                raise RuntimeError("Unknown resource type: %s" % str(resource))

        self.resource_creation_logger.destroy()
