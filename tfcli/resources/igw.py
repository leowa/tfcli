from .base import BaseResource


class Igw(BaseResource):
    """ igw (internet gateway) resource to generate from current region
    """

    def __init__(self, logger=None, indexes=None):
        super().__init__(logger)

    @classmethod
    def ignore_attrbute(cls, key, value):
        if key in ["id", "owner_id"]:
            return True
        return False

    @classmethod
    def included_resource_types(cls):
        """resource types for this resource and its derived resources
        """
        return [
            "aws_internet_gateway"
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        ec2 = self.session.client("ec2")
        igws = ec2.describe_internet_gateways()["InternetGateways"]
        for item in igws:
            # find name in tags, fall back to id if not exists
            _name = _id = item["InternetGatewayId"]
            for tag in item["Tags"]:
                if tag["Key"] == "Name":
                    _name = tag["Value"]
                    break
            yield "aws_internet_gateway", _name, _id
