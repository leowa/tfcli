from .base import BaseResource


class Rds(BaseResource):
    """ aws_db_instance to generate from current region
    """

    def __init__(self, logger=None, indexes=None):
        super().__init__(logger)
        self.indexes = indexes

    @classmethod
    def ignore_attrbute(cls, key, value):
        if key in ["id", "owner_id", "arn", "unique_id"] + [
            "hosted_zone_id",
            "resource_id",
            "address",
            "endpoint",
            "status",
        ]:
            return True
        return False

    @classmethod
    def included_resource_types(cls):
        """resource types for this resource and its derived resources
        """
        return ["aws_db_instance", "aws_db_subnet_group", "aws_db_parameter_group"]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        rds = self.session.client("rds")
        items = rds.describe_db_instances()["DBInstances"]
        for i, one in enumerate(items):
            _id = one["DBInstanceIdentifier"]
            if not self.indexes or i in self.indexes:
                yield self.included_resource_types()[0], _id, _id

        items = rds.describe_db_subnet_groups()["DBSubnetGroups"]
        for i, one in enumerate(items):
            name = one["DBSubnetGroupName"]
            _id = one["DBSubnetGroupArn"]
            if not self.indexes or i in self.indexes:
                yield self.included_resource_types()[1], name, name

        # NOTE: skip DBParameterGroups due to the following issue:
        # https://github.com/terraform-providers/terraform-provider-aws/issues/12144
        # `only lowercase alphanumeric characters and hyphens allowed in parameter group "name"``
        # items = rds.describe_db_parameter_groups()["DBParameterGroups"]
        # for i, one in enumerate(items):
        #     name = one["DBParameterGroupName"]
        #     if not self.indexes or i in self.indexes:
        #         yield self.included_resource_types()[1], normalize_identity(name), name
