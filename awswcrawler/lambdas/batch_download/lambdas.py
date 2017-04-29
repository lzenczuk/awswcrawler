import random
import string
import boto3
import datetime
import logging


def create_batch_endpoint(event, context):
    """
    Initialize new batch download flow.
    :param event: http event
    :param context: 
    :return: new batch id
    """

    logger = logging.getLogger("create_batch_endpoint")
    logger.error(event)

    if 'queryStringParameters' not in event:
        return {'error_message': "Missing query parameters."}

    query_params = event['queryStringParameters']

    ### Validate params
    start_id_str = query_params['start_id']
    if start_id_str is None:
        return {'error_message': "Missing start_id parameter."}
    try:
        start_id = long(start_id_str)
    except ValueError:
        return {'error_message': "start_id is not a long number."}

    if start_id <= 0:
        return {'error_message': "start_id have to be bigger then 0."}

    end_id_str = query_params['end_id']
    if end_id_str is None:
        return {'error_message': "Missing end_id parameter."}
    try:
        end_id = long(end_id_str)
    except ValueError:
        return {'error_message': "end_id is not a long number."}

    if end_id <= 0:
        return {'error_message': "end_id have to be bigger then 0."}

    ### Generate batch id
    batch_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))

    ### Create batch entry in db
    client = boto3.client('dynamodb')
    client.put_item(
        TableName='batches',
        Item={
            "batch_id": {
                'N': batch_id
            },
            "create_time": {
                'S': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S%z")
            },
            "start_id": {
                'N': start_id
            },
            "end_id": {
                'N': end_id
            },
            "status": {
                'S': "REQUEST"
            }
        }
    )

    return {"batch_id": batch_id}


def create_batch_download_stack(event, context):
    return "sdfdss"


def generate_batch_requests(event, context):
    return "lklk"


def batch_dawnload(event, context):
    return "lklkjl"


def delete_batch_download_stack(event, context):
    return "lkjhlkjl"
