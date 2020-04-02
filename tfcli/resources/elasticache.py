from .base import BaseResource


class Ecc(BaseResource):
    """ elasticache clusterresource to generate from current region
    """

    def __init__(self, logger=None):
        super().__init__(logger)

    @classmethod
    def ignore_attrbute(cls, key, value):
        if key in ["id", "owner_id", "arn"] + \
                ["replication_group_id", "cache_nodes",
                 "cluster_address", "configuration_endpoint"]:
            return True
        return False

    @classmethod
    def included_resource_types(cls):
        """resource types for this resource and its derived resources
        """
        return [
            "aws_elasticache_cluster",
            "aws_elasticache_subnet_group",
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        ecc = self.session.client("elasticache")
        items = ecc.describe_cache_clusters()["CacheClusters"]
        for one in items:
            _id = one["CacheClusterId"]
            yield "aws_elasticache_cluster", _id, _id
        items = ecc.describe_cache_subnet_groups()["CacheSubnetGroups"]
        for one in items:
            _name = one["CacheSubnetGroupName"]
            yield "aws_elasticache_subnet_group", _name, _name
