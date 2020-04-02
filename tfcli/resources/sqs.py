from .base import BaseResource


class Sqs(BaseResource):
    """ aws_sqs_queue to generate from current region
    """

    def __init__(self, logger=None, indexes=None):
        super().__init__(logger)
        self.indexes = indexes

    @classmethod
    def ignore_attrbute(cls, key, value):
        if key in ["id", "owner_id", "arn", "unique_id"]:
            return True
        return False

    @classmethod
    def included_resource_types(cls):
        """resource types for this resource and its derived resources
        """
        return [
            "aws_sqs_queue",
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        sqs = self.session.client("sqs")
        items = sqs.list_queues()["QueueUrls"]
        for i, one in enumerate(items):
            name = one.split('/')[-1]
            if not self.indexes or i in self.indexes:
                yield self.included_resource_types()[0], name, one
