import boto3


def get_bucket(name):
    client = boto3.client('s3')
    response = client.list_buckets()

    b = next((bucket for bucket in response['Buckets'] if bucket['Name'] == name), None)
    if b is None:
        return None

    return S3Bucket(name)


def create_bucket(name, acl='private'):
    client = boto3.client('s3')
    current_region = boto3.session.Session().region_name

    client.create_bucket(
            ACL=acl,
            Bucket=name,
            CreateBucketConfiguration={
                'LocationConstraint': current_region
            }
        )

    return get_bucket(name)


def delete_bucket(name):
    client = boto3.client('s3')
    bucket = get_bucket(name)

    if bucket is not None:
        bucket.delete_all_object()

        client.delete_bucket(Bucket=name)


class S3Bucket:
    def __init__(self, name):
        self.name = name
        self.client = boto3.client('s3')

    def is_empty(self):
        print(self.list_objects())
        return len(self.list_objects()) == 0

    def list_objects(self):
        response = self.client.list_objects(
            Bucket=self.name
        )

        if 'Contents' not in response:
            return []

        return [c['Key'] for c in response['Contents']]

    def delete_object(self, keys):

        if isinstance(keys, list):
            objects = [{'Key': k} for k in keys]
        else:
            objects = [{'Key': keys}]

        self.client.delete_objects(
            Bucket=self.name,
            Delete={
                'Objects': objects,
                'Quiet': True
            }
        )

    def delete_all_object(self):
        self.delete_object(self.list_objects())

    def upload_file(self, file_path, bucket_key, content_type=None):
        extra_args = {}

        if content_type is not None:
            extra_args['ContentType'] = content_type

        with open(file_path, 'rb') as data:
            self.client.upload_fileobj(data, self.name, bucket_key, ExtraArgs=extra_args)

    def write_string(self, file_path, content, content_type=None):
        if content_type is not None:
            self.client.put_object(
                Body=content,
                Bucket=self.name,
                Key=file_path,
                ContentType=content_type
            )
        else:
            self.client.put_object(
                Body=content,
                Bucket=self.name,
                Key=file_path
            )

    def read_string(self, file_path):
        response = self.client.get_object(
            Bucket=self.name,
            Key=file_path
        )

        return response['Body'].read()

    def config_website(self, error_document_key="error.html", index_document_suffix="index.html"):
        self.client.put_bucket_website(
            Bucket=self.name,
            WebsiteConfiguration={
                'ErrorDocument': {
                    'Key': error_document_key
                },
                'IndexDocument': {
                    'Suffix': index_document_suffix
                }
            }
        )

    def get_website_url(self):
        current_region = boto3.session.Session().region_name

        return "http://%s.s3-website-%s.amazonaws.com" % (self.name, current_region)

    def set_policy(self, policy_json):
        self.client.put_bucket_policy(
            Bucket=self.name,
            Policy=policy_json
        )



