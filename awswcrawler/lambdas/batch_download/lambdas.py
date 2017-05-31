import logging

import uuid

import awswcrawler.aws.ddb as ddb
import awswcrawler.aws.sqs as sqs
import awswcrawler.aws.lambdas as lbs
from aws.resource_manager import S3FolderResourceCreationLogger, ResourceManager


def create_batch_endpoint(event, context):
    """
    Initialize new batch download flow.
    :param event: http event
    :param context: 
    :return: new batch id
    """

    logger = logging.getLogger("create_batch_endpoint")
    logger.error(event)

    if 'start_id' not in event or 'end_id' not in event:
        return {"error_message": "Missing parameters. Expecting start_id and end_id, was %s" % str(event)}

    try:
        start_id = long(event['start_id'])
        end_id = long(event['end_id'])
    except ValueError:
        return {'error_message': "Can not parse start_id and end_id to long from %s" % str(event)}

    if start_id <= 0:
        return {'error_message': "start_id have to be bigger then 0, was %s" % str(start_id)}

    if end_id <= 0:
        return {'error_message': "end_id have to be bigger then 0, was %s" % str(end_id)}

    if start_id > end_id:
        tmp = start_id
        start_id = end_id
        end_id = tmp

    batch_id = str(uuid.uuid4())

    batches = ddb.get_table("batches")
    batches.insert_item({"batch_id": batch_id, "start_id": start_id, "end_id": end_id})

    rcl = S3FolderResourceCreationLogger("build", "batch_resources_%s" % batch_id)
    rm = ResourceManager(rcl)

    batch = rm.create_ddb_table("download_batch_%s" % batch_id, "batch_id", 'S', "download_id", "N")
    queue = rm.create_standard_sqs_queue("download_batch_%s_q" % batch_id)

    self = lbs.get_lambda("awswcrawler.lambdas.batch_download.lambdas.create_batch_endpoint")
    role = self.get_role()
    role.add_permission(batch.get_arn(), ddb.write_actions())
    role.add_permission(queue.get_arn(), sqs.write_actions())

    for d_id in range(start_id, end_id):
        print(d_id)
        batch.insert_item({"batch_id": batch_id, "download_id": d_id})
        queue.send_message({"batch_id": batch_id, "download_id": d_id})

    return {"batch_id": batch_id}


def create_batch_download_stack(event, context):
    return "sdfdss"


def generate_batch_requests(event, context):
    return "lklk"


def batch_dawnload(event, context):
    return "lklkjl"


def delete_batch_download_stack(event, context):
    return "lkjhlkjl"
