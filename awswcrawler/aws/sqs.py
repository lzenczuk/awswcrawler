import json

import boto3


def create_standard_sqs_queue(name):
    client = boto3.client('sqs')
    response = client.create_queue(
        QueueName=name
    )

    return Sqs(response['QueueUrl'])


def delete_sqs_queue(queue_url):
    client = boto3.client('sqs')
    client.delete_queue(
        QueueUrl=queue_url
    )


class Sqs:
    def __init__(self, queue_url):
        self.queue_url = queue_url
        self.queue = boto3.resource('sqs').Queue(queue_url)

    def send(self, message):
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

