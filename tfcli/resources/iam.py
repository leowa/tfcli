from .base import BaseResource
from ..filters import normalize_identity


class Iamg(BaseResource):
    """ IAM Group , group membership and group policy to generate from current region
    """

    def __init__(self, logger=None):
        super().__init__(logger)

    @classmethod
    def ignore_attrbute(cls, key, value):
        if key in ["id", "owner_id", "arn", "unique_id"]:
            return True
        return False

    def amend_attributes(self, _type, _name, attributes: dict):
        """ make some needed change for attributes to some type of resource, such as adding default ones, or modify existing one

        :param _type: resource type
        :param _name: resource name
        """
        if _type == "aws_iam_group_membership":
            attributes["name"] = "{}-group-membership".format(_name)
            attributes["group"] = _name
            iam = self.session.client("iam")
            users = iam.get_group(GroupName=_name)["Users"]
            attributes["users"] = [_["UserName"] for _ in users]
        return attributes

    @classmethod
    def included_resource_types(cls):
        """resource types for this resource and its derived resources
        """
        return [
            "aws_iam_group",
            "aws_iam_group_policy",
            "aws_iam_group_membership",
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        iam = self.session.client("iam")
        groups = iam.list_groups()["Groups"]
        for one in groups:
            group_name = one["GroupName"]
            yield "aws_iam_group", group_name, group_name

            # TODO: need to a way to directly add this to state file, otherwise, plan will show diff for membership
            # yield "aws_iam_group_membership", group_name, group_name

            # list group policies
            gps = iam.list_group_policies(GroupName=group_name)["PolicyNames"]
            for gp in gps:
                gp_name = normalize_identity("{}_{}".format(group_name, gp))
                gp_id = "{}:{}".format(group_name, gp)
                yield "aws_iam_group_policy", gp_name, gp_id
