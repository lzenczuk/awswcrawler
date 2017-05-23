import logging

import uuid

from awswcrawler.aws.ddb import get_table


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
        end_id = long(event['start_id'])
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

    batches = get_table("batches")
    batches.insert_item({"batch_id": batch_id, "start_id": start_id, "end_id": end_id})

    return {"batch_id": batch_id}


def create_batch_download_stack(event, context):
    return "sdfdss"


def generate_batch_requests(event, context):
    return "lklk"


def batch_dawnload(event, context):
    return "lklkjl"


def delete_batch_download_stack(event, context):
    return "lkjhlkjl"
