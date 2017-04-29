import unittest

from aws.cf.stack import StackTemplate
from aws.cf.s3 import S3Template


class TestCf(unittest.TestCase):
    def test_empty_stack(self):
        stack = StackTemplate()
        template = stack.cf_resource()
        self.assertDictEqual(template, {'AWSTemplateFormatVersion': '2010-09-09', 'Resources': {}})

    def test_stack_with_one_s3_bucket(self):
        stack = StackTemplate()
        s3 = S3Template("app_package")
        stack.add_resource("deployment_bucket", s3)

        template = stack.cf_resource()
        self.assertDictEqual(template, {
            'AWSTemplateFormatVersion': '2010-09-09',
            'Resources': {
                'deployment_bucket': {
                    'Type': 'AWS::S3::Bucket',
                    'Properties': {
                        'BucketName': 'app_package'
                    }
                }
            }})

    def test_stack_with_two_s3_bucket(self):
        stack = StackTemplate()
        s31 = S3Template("app_package")
        s32 = S3Template("files_storage")
        stack.add_resource("deployment_bucket1", s31)
        stack.add_resource("deployment_bucket2", s32)

        template = stack.cf_resource()

        print(template)

        self.assertDictEqual(template, {
            'AWSTemplateFormatVersion': '2010-09-09',
            'Resources': {
                'deployment_bucket1': {
                    'Type': 'AWS::S3::Bucket',
                    'Properties': {
                        'BucketName': 'app_package'
                    }
                },
                'deployment_bucket2': {
                    'Type': 'AWS::S3::Bucket',
                    'Properties': {
                        'BucketName': 'files_storage'
                    }
                }
            }})


if __name__ == '__main__':
    unittest.main()
