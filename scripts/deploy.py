import json
import os
import boto3
import string
import random
import shutil
from distutils.dir_util import copy_tree as cp
from distutils.dir_util import remove_tree as rm
import zipfile

from aws.cf.s3 import S3Template
from aws.cf.stack import StackTemplate
from aws.cf.lambdas import LambdaTemplate


def zip_dir(path, ziph):
    for root, dirs, files in os.walk(path):
        relative_root = root.replace(path, "")
        for f in files:
            ziph.write(os.path.join(root, f), os.path.join(relative_root, f))


project_directory = "/home/dev/Documents/python-sandbox/awswcrawler"
project_code_directory = project_directory + "/awswcrawler"

venv_dir = project_directory + "/venv"

tmp_root_dir = "/tmp"
building_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
building_dir = tmp_root_dir + "/app_build_" + building_id

if os.path.exists(building_dir):
    os.removedirs(building_dir)

os.mkdir(building_dir)

shutil.copytree(project_code_directory, building_dir + "/awswcrawler")
cp(venv_dir + "/lib/python2.7/site-packages", building_dir)

app_file_path = 'app.zip'

zipf = zipfile.ZipFile(app_file_path, 'w', zipfile.ZIP_DEFLATED)
zip_dir(building_dir, zipf)
zipf.close()

rm(building_dir)

cf_client = boto3.client('cloudformation')

# Get stack id if exists -----------------------
response = cf_client.describe_stacks()
stack_id = None
stack = next((st for st in response['Stacks'] if st['StackName'] == "deployStack"), None)
if stack is not None:
    stack_id = stack['StackId']

# delete stack -----------------------
if stack_id is not None:
    print("Not None")
    waiter = cf_client.get_waiter('stack_delete_complete')
    cf_client.delete_stack(StackName=stack_id)
    print("waiting")
    waiter.wait(StackName=stack_id)
    print("Done!")

deploy_bucket_name = "com.github.lzenczuk.awswcrawler.appdeploybucket"
# deploy new stack -----------------------
deployStackTemplate = StackTemplate()
deployStackTemplate.add_resource("appDeployBucket", S3Template(deploy_bucket_name))
temp = deployStackTemplate.cf_resource()
json_template = json.dumps(temp)
waiter = cf_client.get_waiter('stack_create_complete')
response = cf_client.create_stack(
    StackName="deployStack",
    TemplateBody=json_template
)
print("Waiting for deploy")
waiter.wait(
    StackName="deployStack"
)
print("Deploy done!")

bucket_path = "app.zip"

s3_client = boto3.client('s3')
with open(app_file_path, 'rb') as data:
    s3_client.upload_fileobj(data, deploy_bucket_name, bucket_path)

######################################################################################
print("---------------------> app stack deployment")
app_stack_template = StackTemplate()
lambda1 = LambdaTemplate("testLambda",
                         "awscrawler.lambda.batch_download.lambdas::create_batch_endpoint",
                          deploy_bucket_name,
                         "app.zip")
app_stack_template.add_resource("appLambdaResource", lambda1)
temp = app_stack_template.cf_resource()
print(temp)
json_template = json.dumps(temp)
response = cf_client.create_stack(
    StackName="appStack",
    TemplateBody=json_template
)
print("Waiting for deploy")
waiter.wait(
    StackName="appStack"
)
print("Deploy done!")
