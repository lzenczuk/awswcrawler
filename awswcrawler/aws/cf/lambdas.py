class LambdaTemplate:
    def __init__(self, name, handler, bucket_name, bucket_app_path):
        """
        CloudFormation template for python lambda function
        :param name: name of lambda function
        :param handler: python function in format: package::function
        :param bucket_name: bucket containing application zip file  
        :param bucket_app_path: path in a bucket to application zip file 
        """
        self.name = name
        self.handler = handler
        self.bucket_name = bucket_name
        self.bucket_app_path = bucket_app_path

    def cf_resource(self):
        cfr = {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "Code": {
                    "S3Bucket": self.bucket_name,
                    "S3Key": self.bucket_app_path
                },
                "FunctionName": self.name,
                "Handler": self.handler,
                "Role": "arn:aws:iam::039898779445:role/lambda_basic_execution",
                "Runtime": "python2.7",
                "MemorySize": 256,
                "Timeout": 200
            }
        }

        return cfr