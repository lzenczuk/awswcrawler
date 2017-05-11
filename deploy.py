from aws.rest import Rest
from deploy.package import package_app
import time
import awswcrawler.aws.s3 as s3
from awswcrawler.aws.lambdas import delete_lambda
from awswcrawler.aws.lambdas import create_lambda

build_number = timestamp = int(time.time())

deploy_bucket_name = "com.github.lzenczuk.awswcrawler.deploy" + str(build_number)

print("Packaging application")
package_app("app.zip", "build", "venv", "awswcrawler", "deploy")

print("Creating deploy bucket: " + deploy_bucket_name)
s3.delete_bucket(deploy_bucket_name)
deploy_bucket = s3.create_bucket(deploy_bucket_name)

print("Uploading application package to deployment bucket")
deploy_bucket.upload_file("build/app.zip", "app.zip")

delete_lambda("awswcrawler.lambdas.batch_download.lambdas.create_batch_endpoint")
lb = create_lambda(
    "awswcrawler.lambdas.batch_download.lambdas.create_batch_endpoint",
    deploy_bucket_name,
    "app.zip",
    "arn:aws:iam::039898779445:role/lambda_basic_execution"
)

api = Rest("test")
api.map_lambda("GET", "api/users/{user_id}", lb)
api.map_lambda("POST", "api/users/{user_id}", lb)
api.map_lambda("GET", "api/users/{user_id}/tasks", lb)
api.map_lambda("POST", "api/users/{user_id}/tasks?start_id={!start_id}&end_id={!end_id}", lb)
api.deploy("dev")
