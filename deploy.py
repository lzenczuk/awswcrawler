import time

import awswcrawler.aws.s3 as s3
from aws import ddb
from aws.ddb import delete_table, create_table_with_pk
from aws.rest import Rest, delete_rest_api
from aws.role import create_role, delete_role
from awswcrawler.aws.lambdas import create_lambda
from awswcrawler.aws.lambdas import delete_lambda
from deploy.package import package_app

build_number = timestamp = int(time.time())

deploy_bucket_name = "com.github.lzenczuk.awswcrawler.deploy" + str(build_number)

print("Packaging application")
package_app("app.zip", "build", "venv", "awswcrawler", "deploy")

print("Creating deploy bucket: " + deploy_bucket_name)
s3.delete_bucket(deploy_bucket_name)
deploy_bucket = s3.create_bucket(deploy_bucket_name)

print("Uploading application package to deployment bucket")
deploy_bucket.upload_file("build/app.zip", "app.zip")

print("Creating dynamodb")
delete_table("batches")
batches = create_table_with_pk("batches", "batch_id", "S")

print("Creating role")
delete_role("test_tmp_role")
lambda_role = create_role("test_tmp_role")
lambda_role.add_permission("*", ddb.ddb_actions())
lambda_role.add_permission(batches.get_arn(), ddb.read_actions())
lambda_role.add_permission(batches.get_arn(), ddb.write_actions())

print("Creating lambda")
delete_lambda("awswcrawler.lambdas.batch_download.lambdas.create_batch_endpoint")
lb = create_lambda(
    "awswcrawler.lambdas.batch_download.lambdas.create_batch_endpoint",
    deploy_bucket_name,
    "app.zip",
    lambda_role.get_arn()
)

print("Creating api gateway")
delete_rest_api("batch_api")
api = Rest("batch_api")
api.map_lambda("POST", "batches?start_id={!start_id}&end_id={!end_id}", lb)
api.deploy("dev")


