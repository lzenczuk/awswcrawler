import json

import boto3
import time
import uuid


def create_role(name):
    client = boto3.client('iam')

    if is_role_exists(name):
        raise RuntimeError("Can not create role '%s'. Role already exists." % name)

    policy_document = {
        "Version": "2012-10-17",
        "Statement": {
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }
    }

    client.create_role(RoleName=name, AssumeRolePolicyDocument=json.dumps(policy_document))
    for x in range(1, 10):
        if is_role_exists(name):

            # Role exists but for some reason lambda will throw exception with out this sleep
            print("Waiting for lambda role to be replicated... 10s")
            time.sleep(10)

            return Role(name)

        print("Waiting for lambda role to be created... 2s")
        time.sleep(2)

    raise RuntimeError("Timeout waiting for role to be created")


def get_role(name):
    if is_role_exists(name):
        return Role(name)
    else:
        return None


def get_role_name_by_arn(role_arn):
    client = boto3.client('iam')
    for role in client.list_roles()['Roles']:
        if role['Arn'] == role_arn:
            return role['RoleName']

    return None


def is_role_exists(name):
    client = boto3.client('iam')
    for role in client.list_roles()['Roles']:
        if role['RoleName'] == name:
            return True

    return False


def delete_role(name):
    if is_role_exists(name):
        client = boto3.client('iam')

        for policy_name in client.list_role_policies(RoleName=name)['PolicyNames']:
            client.delete_role_policy(
                RoleName=name,
                PolicyName=policy_name
            )

        boto3.client('iam').delete_role(RoleName=name)

        for x in range(1, 5):
            if is_role_exists(name):
                time.sleep(2)
            else:
                return

        raise RuntimeError("Timeout waiting for role to be created")


def role_actions():
    return [
        "iam:ListRoles",
    ]


def write_actions():
    return [
        "iam:PutRolePolicy"
    ]


class Role:
    def __init__(self, name):
        self.client = boto3.client('iam')
        self.name = name

    def add_permission(self, resource, actions):
        policy_name = "role."+self.name + ".policy." + str(uuid.uuid4())

        self.client.put_role_policy(
            RoleName=self.name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": actions,
                        "Resource": resource
                    }
                ]}),
        )

        print("Waiting to propagate new permissions... 10s")
        time.sleep(10)

    def get_arn(self):
        account_id = boto3.client('sts').get_caller_identity().get('Account')
        arn = "arn:aws:iam::%s:role/%s" % (account_id, self.name)
        return arn


