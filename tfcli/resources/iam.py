from .base import BaseResource
from ..filters import normalize_identity


class Group(BaseResource):
    """IAM Group , group membership and group policy to generate from current region"""

    def __init__(self, logger=None):
        super().__init__(logger)

    @classmethod
    def ignore_attrbute(cls, key, value):
        if key in ["id", "owner_id", "arn", "unique_id"]:
            return True
        return False

    def amend_attributes(self, _type, _name, attributes: dict):
        """make some needed change for attributes to some type of resource, such as adding default ones, or modify existing one

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
        """resource types for this resource and its derived resources"""
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
        # filtered policy list to exclude AWS managed policies
        local_policies = set()
        ret = iam.list_policies(Scope="Local", MaxItems=1000)
        local_policies.update([_["PolicyName"] for _ in ret["Policies"]])
        while ret["IsTruncated"]:
            ret = iam.list_policies(Scope="Local", MaxItems=1000, Marker=ret["Marker"])
            local_policies.update([_["PolicyName"] for _ in ret["Policies"]])
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
            for a in iam.list_attached_group_policies(GroupName=group_name)[
                "AttachedPolicies"
            ]:
                aname, aarn = a["PolicyName"], a["PolicyArn"]
                yield (
                    "aws_iam_group_policy_attachment",
                    "{}-{}".format(group_name, aname),
                    "{}/{}".format(group_name, aarn),
                )
                if aname in local_policies:
                    yield "aws_iam_policy", aname, aarn


class Role(BaseResource):
    """IAM Role"""

    def __init__(self, logger=None):
        super().__init__(logger)

    @classmethod
    def ignore_attrbute(cls, key, value):
        if key in ["id", "owner_id", "arn", "unique_id"]:
            return True
        return False

    def amend_attributes(self, _type, _name, attributes: dict):
        """make some needed change for attributes to some type of resource, such as adding default ones, or modify existing one

        :param _type: resource type
        :param _name: resource name
        """
        # if _type == "aws_iam_group_membership":
        #     attributes["name"] = "{}-group-membership".format(_name)
        #     attributes["group"] = _name
        #     iam = self.session.client("iam")
        #     users = iam.get_group(GroupName=_name)["Users"]
        #     attributes["users"] = [_["UserName"] for _ in users]
        return attributes

    @classmethod
    def included_resource_types(cls):
        """resource types for this resource and its derived resources"""
        return [
            "aws_iam_role",
            "aws_iam_policy",
            "aws_iam_role_policy_attachment",
            "aws_iam_instance_profile",
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        iam = self.session.client("iam")
        # filtered policy list to exclude AWS managed policies
        local_policies = set()
        ret = iam.list_policies(Scope="Local", MaxItems=1000)
        local_policies.update([_["PolicyName"] for _ in ret["Policies"]])
        while ret["IsTruncated"]:
            ret = iam.list_policies(Scope="Local", MaxItems=1000, Marker=ret["Marker"])
            local_policies.update([_["PolicyName"] for _ in ret["Policies"]])

        roles = []
        ret = iam.list_roles(MaxItems=1000)
        roles.extend(ret["Roles"])
        while ret["IsTruncated"]:
            ret = iam.list_roles(MaxItems=1000, Marker=ret.Marker)
            roles.extend(ret["Roles"])
        for one in roles:
            name = one["RoleName"]
            normalized_name = normalize_identity(name)
            yield "aws_iam_role", normalized_name, name
            attached = iam.list_attached_role_policies(RoleName=name)
            for a in attached["AttachedPolicies"]:
                aname, aarn = a["PolicyName"], a["PolicyArn"]
                yield (
                    "aws_iam_role_policy_attachment",
                    "{}-{}".format(normalized_name, aname),
                    "{}/{}".format(normalized_name, aarn),
                )
                if aname in local_policies:
                    yield "aws_iam_policy", aname, aarn
            for a in iam.list_instance_profiles_for_role(RoleName=name)[
                "InstanceProfiles"
            ]:
                name = a["InstanceProfileName"]
                yield "aws_iam_instance_profile", name, name
