from .base import BaseResource


class Sns(BaseResource):
    """ aws_sns_topic, and aws_sns_topic_subscription to generate from current region
    """

    def __init__(self, logger=None, indexes=None):
        super().__init__(logger)
        self.indexes = indexes

    def amend_attributes(self, _type, _name, attributes: dict):
        """ make some needed change for attributes to some type of resource, such as adding default ones, or modify existing one

        :param _type: resource type
        :param _name: resource name
        """
        if "availability_zone" in attributes and "availability_zone_id" in attributes:
            del attributes["availability_zone_id"]
        return attributes

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
            "aws_sns_topic",
            "aws_sns_topic_subscription",
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        sns = self.session.client("sns")
        items = sns.list_topics()["Topics"]
        for i, one in enumerate(items):
            arn = one["TopicArn"]
            name = arn.split(':')[-1]
            if not self.indexes or i in self.indexes:
                yield self.included_resource_types()[0], name, arn

        # NOTE: "email" is not supported as subscription protocal
        # ref: https://www.terraform.io/docs/providers/aws/r/sns_topic_subscription.html#protocols-supported
        items = sns.list_subscriptions()["Subscriptions"]
        for i, one in enumerate(items):
            arn = one["SubscriptionArn"]
            name = arn.split(':')[-1]
            if not self.indexes or i in self.indexes \
                    and one["Protocol"] not in ["email", "email-json"]:
                yield self.included_resource_types()[1], name, arn
