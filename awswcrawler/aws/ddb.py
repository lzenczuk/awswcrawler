import boto3
import time
from boto3.dynamodb.conditions import Key


def get_table(name):
    client = boto3.client('dynamodb')

    if is_table_exists(name):
        response = client.describe_table(
            TableName=name
        )

        (pk, sk) = __extract_keys_from_schema_array__(response['Table']['KeySchema'])
        return DDBTable(response['Table']['TableName'], pk, sk)


def is_table_exists(name):
    client = boto3.client('dynamodb')

    t_name = None
    for t in client.list_tables()['TableNames']:
        if t == name:
            t_name = t
            break

    return t_name is not None


def create_table_with_pk(name, pk_name, pk_type, read_capacity=5, write_capacity=5):
    """
    Creates DynamoDB table with only partition key.
    :param name: table name
    :param pk_name: partition key attribute name
    :param pk_type: partition key attribute type S|N|B
    :param read_capacity: number of reads per second
    :param write_capacity: number of writes per second 
    :return: DDBTable
    """
    return create_table_with_pk_and_sk(name, pk_name, pk_type, None, None, read_capacity, write_capacity)


def create_table_with_pk_and_sk(name, pk_name, pk_type, sk_name, sk_type, read_capacity=5, write_capacity=5):
    """
    Creates DynamoDB table with pair partition key and sort key as primary key.
    :param name: table name
    :param pk_name: partition key attribute name
    :param pk_type: partition key attribute type S|N|B
    :param sk_name: sort key attribute name
    :param sk_type: sort key attribute type S|N|B
    :param read_capacity: number of reads per second
    :param write_capacity: number of writes per second 
    :return: DDBTable
    """
    if name is None:
        raise ValueError("Table name can't be None.")

    if pk_name is None or pk_type is None:
        raise ValueError("Partition key and name can't be None")

    attribute_definitions = []
    key_schema = []

    attribute_definitions.append({"AttributeName": pk_name, "AttributeType": pk_type})
    key_schema.append({"AttributeName": pk_name, "KeyType": "HASH"})

    if sk_name is not None:
        if sk_type is None:
            raise ValueError("Sort key type must be specific.")
        else:
            attribute_definitions.append({"AttributeName": sk_name, "AttributeType": sk_type})
            key_schema.append({"AttributeName": sk_name, "KeyType": "RANGE"})

    client = boto3.client('dynamodb')

    response = client.create_table(
        AttributeDefinitions=attribute_definitions,
        TableName=name,
        KeySchema=key_schema,
        ProvisionedThroughput={
            'ReadCapacityUnits': read_capacity,
            'WriteCapacityUnits': write_capacity
        }
    )
    if response['TableDescription']['TableStatus'] == 'ACTIVE':
        print(response)
        (pk, sk) = __extract_keys_from_schema_array__(response['TableDescription']['KeySchema'])
        return DDBTable(response['TableDescription']['TableName'], pk, sk)
    else:
        for x in range(1, 5):
            time.sleep(2)
            response = client.describe_table(
                TableName=name
            )

            if response['Table']['TableStatus'] == 'ACTIVE':
                (pk, sk) = __extract_keys_from_schema_array__(response['Table']['KeySchema'])
                return DDBTable(response['Table']['TableName'], pk, sk)

        raise RuntimeError("Timeout waiting for table to be created")


def __extract_keys_from_schema_array__(schema_array):
    pk_name = None
    sk_name = None

    for sc in schema_array:
        if sc['KeyType'] == 'HASH':
            pk_name = sc['AttributeName']

        if sc['KeyType'] == 'RANGE':
            sk_name = sc['AttributeName']

    return pk_name, sk_name


def delete_table(name):
    client = boto3.client('dynamodb')

    if is_table_exists(name):
        client.delete_table(
            TableName=name
        )


class DDBTable:
    def __init__(self, name, pk_name, sk_name):
        self.name = name
        self.pk_name = pk_name
        self.sk_name = sk_name
        self.table = boto3.resource('dynamodb').Table(name)

    def insert_item(self, item):
        """
        Inserts item to table 
        :param item: dict, have to have pk attribute/s
        :return: 
        """
        self.table.put_item(
            TableName=self.name,
            Item=item
        )

    def insert_items(self, items):
        """
        Inserts multiple items to table
        :param items: array of dict
        :return: 
        """
        with self.table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)

    def fetch_items_by_pk(self, pk_value):
        response = self.table.query(
            KeyConditionExpression=Key(self.pk_name).eq(pk_value)
        )

        return response['Items']

