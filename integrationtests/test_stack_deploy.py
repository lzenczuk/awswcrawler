import unittest

from aws.cf.s3 import S3Template
from aws.cf.stack import StackTemplate


class TestCf(unittest.TestCase):
    def test_deploy_stack(self):
        st = StackTemplate()

        s31 = S3Template("com.github.lzenczuk.aws.app-deploy-storage")
        s32 = S3Template("com.github.lzenczuk.aws.files-storage")\
            .set_access_to_public_read()

        st.add_resource("deploymentBucket1", s31)
        st.add_resource("deploymentBucket2", s32)

        #cfc = CloudFormationClient()
        print("-----------> deploying")
        #stack = cfc.deploy(st, "stackOne")
        print("-----------> done")

        #print(stack.status)

        print("-----------> deleting")
        #stack.delete()
        print("-----------> done")
        #print(stack.status)


if __name__ == '__main__':
    unittest.main()
