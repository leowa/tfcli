from .base import BaseResource
from ..filters import normalize_identity


class Vpc(BaseResource):
    """ vpc resource to generate from current region
    """

    def __init__(self, logger=None):
        super().__init__(logger)

    @classmethod
    def ignore_attrbute(cls, key, value):
        if key in ["id", "owner_id", "arn"] + [
            "default_network_acl_id",
            "default_route_table_id",
            "default_security_group_id",
            "main_route_table_id",
            "dhcp_options_id",
        ]:
            return True
        return False

    @classmethod
    def included_resource_types(cls):
        """resource types for this resource and its derived resources
        """
        return [
            "aws_vpc",
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        ec2 = self.session.client("ec2")
        items = ec2.describe_vpcs()["Vpcs"]
        for one in items:
            _id = one["VpcId"]
            _name = self.get_resource_name_from_tags(one["Tags"]) or _id
            yield "aws_vpc", _name, _id


class Igw(BaseResource):
    """ igw (internet gateway) resource to generate from current region
    """

    def __init__(self, logger=None):
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
        return ["aws_internet_gateway"]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        ec2 = self.session.client("ec2")
        igws = ec2.describe_internet_gateways()["InternetGateways"]
        for item in igws:
            # find name in tags, fall back to id if not exists
            _id = item["InternetGatewayId"]
            _name = self.get_resource_name_from_tags(item["Tags"]) or _id
            yield "aws_internet_gateway", _name, _id


class Elb(BaseResource):
    """ elb resource to generate from current region
    """

    def __init__(self, logger=None):
        super().__init__(logger)

    @classmethod
    def ignore_attrbute(cls, key, value):
        if key in ["arn", "arn_suffix", "zone_id", "dns_name", "vpc_id", "id"]:
            return True
        if key == "access_logs" and not value[0]["enabled"]:
            return True
        return False

    @classmethod
    def included_resource_types(cls):
        """resource types for this resource and its derived resources
        """
        return [
            "aws_alb",
            "aws_alb_listener",
            "aws_alb_listener_certificate",
            "aws_alb_listener_rule",
            "aws_alb_target_group",
            "aws_alb_target_group_attachment",
            "aws_elb",
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        elb = self.session.client("elbv2")
        items = elb.describe_load_balancers()["LoadBalancers"]
        for item in items:
            yield "aws_alb", item["LoadBalancerName"], item["LoadBalancerArn"]


class Eip(BaseResource):
    """ eip resource to generate from current region
    """

    def __init__(self, logger=None, indexes=None):
        super().__init__(logger)
        self.indexes = (
            indexes  # limit resource indexes to return, primarily for speeding testing
        )

    @classmethod
    def ignore_attrbute(cls, key, value):
        if key in ["id", "owner_id", "arn"] + [
            "domain",
            "public_dns",
            "private_dns",
            "association_id",
            "public_ip",
            "private_ip",
        ]:
            return True
        return False

    @classmethod
    def included_resource_types(cls):
        """resource types for this resource and its derived resources
        """
        return [
            "aws_eip",
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        ec2 = self.session.client("ec2")
        items = ec2.describe_addresses()["Addresses"]
        for i, one in enumerate(items):
            if (not self.indexes) or (i in self.indexes):
                _id = one["AllocationId"]
                yield "aws_eip", _id, _id


class Nif(BaseResource):
    """ aws_network_interface to generate from current region
    """

    def __init__(self, logger=None, indexes=None):
        super().__init__(logger)
        self.indexes = indexes

    @classmethod
    def ignore_attrbute(cls, key, value):
        if key in ["id", "owner_id", "arn", "unique_id"] + [
            "mac_address",
            "private_dns_name",
        ]:
            return True
        return False

    def amend_attributes(self, _type, _name, attributes: dict):
        """ make some needed change for attributes to some type of resource, such as adding default ones, or modify existing one

        :param _type: resource type
        :param _name: resource name
        """
        if "attachment" in attributes:
            for a in attributes["attachment"]:
                if "attachment_id" in a:
                    del a["attachment_id"]
        return attributes

    @classmethod
    def included_resource_types(cls):
        """resource types for this resource and its derived resources
        """
        return [
            "aws_network_interface",
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        ec2 = self.session.client("ec2")
        items = ec2.describe_network_interfaces()["NetworkInterfaces"]
        for i, one in enumerate(items):
            _id = one["NetworkInterfaceId"]
            # HACK: skip those managed by amazon-rds, with Attachment.InstanceId
            if (not self.indexes or i in self.indexes) and (
                "RequesterId" not in one or one["RequesterId"] != "amazon-rds"
            ):
                yield self.included_resource_types()[0], _id, _id


class Nacl(BaseResource):
    """ aws_network_interface to generate from current region
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
            "aws_network_acl",
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        ec2 = self.session.client("ec2")
        items = ec2.describe_network_acls()["NetworkAcls"]
        for i, one in enumerate(items):
            _id = one["NetworkAclId"]
            if not self.indexes or i in self.indexes:
                yield self.included_resource_types()[0], _id, _id


class Rt(BaseResource):
    """ aws_route_table to generate from current region
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
            "aws_route_table",
            "aws_route_table_association",
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        ec2 = self.session.client("ec2")
        items = ec2.describe_route_tables()["RouteTables"]
        for i, one in enumerate(items):
            _id = one["RouteTableId"]
            if not self.indexes or i in self.indexes:
                yield self.included_resource_types()[0], _id, _id
                if "Associations" in one:
                    for ass in one["Associations"]:
                        if ass["Main"]:  # no need to add association for Main one
                            continue
                        a_name = ass["RouteTableAssociationId"]
                        a_id = "{}/{}".format(
                            ass["SubnetId"] if "SubnetId" in ass else ass["GatewayId"],
                            _id,
                        )
                        yield self.included_resource_types()[1], a_name, a_id


class Sg(BaseResource):
    """ aws_security_group to generate from current region
    """

    def __init__(self, logger=None, indexes=None):
        super().__init__(logger)
        self.indexes = indexes

    def amend_attributes(self, _type, _name, attributes: dict):
        """ make some needed change for attributes to some type of resource, such as adding default ones, or modify existing one

        :param _type: resource type
        :param _name: resource name
        """
        if (
            _type == "aws_security_group_rule"
            and "self" in attributes
            and "source_security_group_id" in attributes
        ):
            del attributes["source_security_group_id"]
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
            "aws_security_group",
            "aws_security_group_rule",
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        ec2 = self.session.client("ec2")
        items = ec2.describe_security_groups()["SecurityGroups"]
        for i, one in enumerate(items):
            name, _id, = one["GroupName"], one["GroupId"]
            if not self.indexes or i in self.indexes:
                yield self.included_resource_types()[0], name, _id


class Subnet(BaseResource):
    """ aws_subnet to generate from current region
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
            "aws_subnet",
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        ec2 = self.session.client("ec2")
        items = ec2.describe_subnets()["Subnets"]
        for i, one in enumerate(items):
            _id = one["SubnetId"]
            name = self.get_resource_name_from_tags(one["Tags"])
            if not self.indexes or i in self.indexes:
                yield self.included_resource_types()[0], normalize_identity(
                    "{}-{}".format(_id, name)
                ), _id
