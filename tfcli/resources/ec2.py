from collections import defaultdict
from .base import BaseResource
from ..filters import normalize_identity


class Ec2(BaseResource):
    """ aws_instance to generate from current region
    """

    def __init__(self, logger=None, indexes=None):
        super().__init__(logger)
        self.indexes = indexes

    def amend_attributes(self, _type, _name, attributes: dict):
        """ make some needed change for attributes to some type of resource, such as adding default ones, or modify existing one

        :param _type: resource type
        :param _name: resource name
        """
        if _type == "aws_instance" and "ebs_block_device" in attributes:
            for ebs in attributes["ebs_block_device"]:
                if "volume_id" in ebs:
                    del ebs["volume_id"]
        if _type == "aws_instance" and "root_block_device" in attributes:
            for rb in attributes["root_block_device"]:
                if "volume_id" in rb:
                    del rb["volume_id"]
        return attributes

    @classmethod
    def ignore_attrbute(cls, key, value):
        if key in ["id", "owner_id", "arn", "unique_id"] + [
            "primary_network_interface_id",
            "private_dns",
            "instance_state",
            "public_ip",
            "public_dns",
        ]:
            return True
        return False

    @classmethod
    def included_resource_types(cls):
        """resource types for this resource and its derived resources
        """
        return [
            "aws_instance",
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        ec2 = self.session.client("ec2")
        items = ec2.describe_instances()["Reservations"]
        asgs = defaultdict(list)
        for i, one in enumerate([_ for sub in items for _ in sub["Instances"]]):
            _id = one["InstanceId"]
            name = self.get_resource_name_from_tags(one["Tags"])
            # NOTE: skip those managed by autoscaling
            asg = self.get_value_from_tags(one["Tags"], "aws:autoscaling:groupName")
            if asg:
                asgs[asg].append(_id)
                continue
            if not self.indexes or i in self.indexes:
                yield self.included_resource_types()[0], normalize_identity(name), _id

        if len(asgs):
            self.logger.info(
                "skip instances managed by autoscaling groups.\n{}".format(
                    "\n".join(["{}: {}".format(k, len(v)) for k, v in asgs.items()])
                )
            )
