import time

import awswcrawler.aws.s3 as s3
from aws.ddb import delete_table, create_table_with_pk
from aws.rest import Rest, delete_rest_api
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

print("Creating lambda")
delete_lambda("awswcrawler.lambdas.batch_download.lambdas.create_batch_endpoint")
lb = create_lambda(
    "awswcrawler.lambdas.batch_download.lambdas.create_batch_endpoint",
    deploy_bucket_name,
    "app.zip",
    "arn:aws:iam::039898779445:role/lambda_basic_execution"
)

print("Creating api gateway")
delete_rest_api("batch_api")
api = Rest("batch_api")
api.map_lambda("POST", "batches?start_id={!start_id}&end_id={!end_id}", lb)
api.deploy("dev")

print("Creating dynamodb")
delete_table("batches")
create_table_with_pk("batches", "batch_id", "S")

