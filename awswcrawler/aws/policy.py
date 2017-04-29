import json

import boto3


def create_policy(name, policy_json):
    client = boto3.client('iam')
    response = client.create_policy(
        PolicyName=name,
        PolicyDocument=policy_json,
    )

    return response['Policy']['Arn']


def get_policy_arn(name):
    client = boto3.client('iam')
    response = client.list_policies(
        Scope='Local',
        OnlyAttached=False
    )

    return next((r['Arn'] for r in response['Policies'] if r['PolicyName'] == name), None)


def delete_policy(name, ignore_when_missing=True):
    client = boto3.client('iam')
    policy_arn = get_policy_arn(name)

    if policy_arn is not None:
        client.delete_policy(
            PolicyArn=policy_arn
        )
    else:
        if not ignore_when_missing:
            raise ValueError("Policy %s not found." % name)


class PolicyBuilder:
    def __init__(self):
        self.statements = []

    def add_statement(self, statement):
        self.statements.append(statement)

    def build(self):
        return {
            "Version": "2012-10-17",
            "Statement": self.statements
        }

    def build_json(self):
        return json.dumps(self.build())


class StatementBuilder:
    def __init__(self, effect="Allow"):
        self.effect = effect
        self.actions = []
        self.resources = []
        self.principal = "*"

    def add_s3_get_object_action(self):
        self.actions.append("s3:GetObject")
        return self

    def set_principal(self, principal):
        self.principal = principal
        return self

    def set_s3_principal(self):
        return self.set_principal('s3.amazonaws.com')

    def set_sns_principal(self):
        return self.set_principal('sns.amazonaws.com')

    def set_apigateway_principal(self):
        return self.set_principal('apigateway.amazonaws.com')

    def add_resource(self, arn):
        self.resources.append(arn)
        return self

    def build(self):
        return {
            'Effect': self.effect,
            'Action': self.actions,
            'Resource': self.resources,
            'Principal': self.principal
        }
