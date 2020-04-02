from .base import BaseResource


class S3(BaseResource):
    """ S3 resource to generate from current region
    """

    def __init__(self, logger=None, indexes=None):
        super().__init__(logger)
        self.indexes = (
            indexes  # limit resource indexes to return, primarily for speeding testing
        )

    @classmethod
    def ignore_attrbute(cls, key, value):
        return key in ["arn", "id", "bucket_regional_domain_name", "bucket_domain_name"]

    @classmethod
    def included_resource_types(cls):
        """resource types for this resource and its derived resources
        """
        return [
            "aws_s3_bucket",
            "aws_s3_bucket_analytics_configuration",
            "aws_s3_bucket_policy",
            "aws_s3_bucket_public_access_block",
            "aws_s3_bucket_object",
            "aws_s3_bucket_notification",
            "aws_s3_bucket_metric",
            "aws_s3_bucket_inventory",
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        s3 = self.session.resource("s3")
        for i, bucket in enumerate(s3.buckets.all()):
            if (not self.indexes) or (i in self.indexes):
                yield "aws_s3_bucket", bucket.name, bucket.name
