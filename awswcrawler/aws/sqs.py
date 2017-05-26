import json

import boto3


def create_standard_sqs_queue(name):
    client = boto3.client('sqs')
    response = client.create_queue(
        QueueName=name
    )

    return Sqs(name, response['QueueUrl'])


def delete_sqs_queue(queue_url):
    client = boto3.client('sqs')
    client.delete_queue(
        QueueUrl=queue_url
    )


def get_sqs_queue(name):
    client = boto3.client('sqs')

    response = client.list_queues(
        QueueNamePrefix=name
    )

    for q_url in response['QueueUrls']:
        q_name = q_url.split("/")[-1]
        if q_name == name:
            return Sqs(name, q_url)

    return None


def sqs_actions():
    return [
        "sqs:ListQueues",
    ]


def sqs_create_actions():
    return [
        "sqs:CreateQueue"
    ]


def write_actions():
    return [
        "sqs:SendMessage",
        "sqs:SendMessageBatch"
    ]


def read_actions():
    return [
        "sqs:ReceiveMessage"
    ]


class Sqs:
    def __init__(self, name, queue_url):
        self.queue_url = queue_url
        self.name = name
        self.queue = boto3.resource('sqs').Queue(queue_url)

    def send_message(self, message):
        self.queue.send_message(
            MessageBody=json.dumps(message)
        )

    def get_message(self):
        messages = self.queue.receive_messages(
            MaxNumberOfMessages=1,
            WaitTimeSeconds=1
        )

        if len(messages) == 0:
            print("No messages. Retry.")
            messages = self.queue.receive_messages(
                MaxNumberOfMessages=1,
                WaitTimeSeconds=1
            )

        if len(messages) == 0:
            return None
        elif len(messages) == 1:
            return json.loads(messages[0].body)
        else:
            raise RuntimeError("Incorrect number of messages receive from queue, expecting 1, was %dn" % len(messages))

    def get_arn(self):
        account_id = boto3.client('sts').get_caller_identity().get('Account')
        region = boto3.session.Session().region_name
        return "arn:aws:sqs:%s:%s:%s" % (region, account_id, self.name)
