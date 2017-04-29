import random
import string

from aws.policy import PolicyBuilder, StatementBuilder
import aws.s3 as s3

prefix = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))
bucket_name = "com.github.lzenczuk.aws.webapp." + prefix

bc = s3.create_bucket(bucket_name, 'public-read')
bc.config_website()
bc.upload_file("../../scripts/index.html", "index.html", "text/html")
bc.upload_file("../../scripts/error.html", "error.html", "text/html")

pb = PolicyBuilder()
pb.add_statement(
    StatementBuilder()
        .add_s3_get_object_action()
        .add_resource("arn:aws:s3:::%s/*" % bucket_name)
        .build()
)

policy_json = pb.build_json()
bc.set_policy(policy_json)

print(bc.get_website_url())
