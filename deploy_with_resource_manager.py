import time
from aws import ddb

from aws.resource_manager import LocalFolderResourceCreationLogger, ResourceManager
from deploy.package import package_app

build_number = timestamp = int(time.time())

deploy_bucket_name = "com.github.lzenczuk.awswcrawler.deploy" + str(build_number)

print("Packaging application")
package_app("app.zip", "build", "venv", "awswcrawler", "deploy")

rcl = LocalFolderResourceCreationLogger("build", "local_resources")
rm = ResourceManager(rcl)

print("Creating deploy bucket: " + deploy_bucket_name)
deploy_bucket = rm.create_bucket(deploy_bucket_name)

print("Uploading application package to deployment bucket")
deploy_bucket.upload_file("build/app.zip", "app.zip")

print("Creating dynamodb")
batches = rm.create_ddb_table("batches", "batch_id", "S")

print("Creating role")
lambda_role = rm.create_lambda_role("test_tmp_role")
lambda_role.add_permission("*", ddb.ddb_actions())
lambda_role.add_permission(batches.get_arn(), ddb.read_actions())
lambda_role.add_permission(batches.get_arn(), ddb.write_actions())

print("Creating lambda")
lb = rm.create_lambda(
    "awswcrawler.lambdas.batch_download.lambdas.create_batch_endpoint",
    deploy_bucket_name,
    "app.zip",
    lambda_role.get_arn()
)

print("Creating api gateway")
api = rm.create_rest_api("batch_api")
api.map_lambda("POST", "batches?start_id={!start_id}&end_id={!end_id}", lb)
api.deploy("dev")

print("Creating sqs")
sqs = rm.create_standard_sqs_queue("test_sqs" + str(build_number))


