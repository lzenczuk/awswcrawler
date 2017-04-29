class S3Template:
    def __init__(self, bucket_name):
        """
        :param bucket_name: (a-z0-9.-) 
        """
        self.bucket_name = bucket_name
        self.access_control = None
        self.versioning = False

    def enable_versioning(self):
        self.versioning = True
        return self

    def disable_versioning(self):
        self.versioning = False
        return self

    def set_access_to_authenticated_read(self):
        self.access_control = "AuthenticatedRead"
        return self

    def set_access_to_aws_exec_read(self):
        self.access_control = "AwsExecRead"
        return self

    def set_access_to_bucket_owner_read(self):
        self.access_control = "BucketOwnerRead"
        return self

    def set_access_to_bucket_owner_full_control(self):
        self.access_control = "BucketOwnerFullControl"
        return self

    def set_access_to_log_delivery_write(self):
        self.access_control = "LogDeliveryWrite"
        return self

    def set_access_to_private(self):
        self.access_control = "Private"
        return self

    def set_access_to_public_read(self):
        self.access_control = "PublicRead"
        return self

    def set_access_to_public_read_write(self):
        self.access_control = "PublicReadWrite"
        return self

    def cf_resource(self):
        cfr = {
            "Type": "AWS::S3::Bucket",
            "Properties": {
                "BucketName": self.bucket_name
            }
        }

        if self.versioning:
            cfr['Properties']['VersioningConfiguration'] = {"Status": "Enabled"}

        if self.access_control is not None:
            cfr['Properties']['AccessControl'] = self.access_control

        return cfr
