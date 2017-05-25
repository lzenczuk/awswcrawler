from aws.ddb import delete_table
from aws.rest import delete_rest_api
from aws.role import delete_role
from awswcrawler.aws.lambdas import delete_lambda

delete_rest_api("batch_api")
delete_lambda("awswcrawler.lambdas.batch_download.lambdas.create_batch_endpoint")
delete_role("test_tmp_role")
delete_table("batches")
