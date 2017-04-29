from aws.policy import PolicyBuilder, StatementBuilder
import awswcrawler.aws.s3 as s3


def create_web_bucket(bucket_name):
    """
    Creates S3 bucket and configure it to host static pages
    :param bucket_name: 
    :return: S3Bucket
    """
    bucket = s3.create_bucket(bucket_name, 'public-read')
    bucket.config_website()

    pb = PolicyBuilder()
    pb.add_statement(
        StatementBuilder()
            .add_s3_get_object_action()
            .add_resource("arn:aws:s3:::%s/*" % bucket_name)
            .build()
    )

    policy_json = pb.build_json()
    bucket.set_policy(policy_json)

    return bucket
