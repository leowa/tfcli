from .base import BaseResource


class Emr(BaseResource):
    """ aws_emr_cluster to generate from current region
    """

    def __init__(self, logger=None, indexes=None):
        super().__init__(logger)
        self.indexes = indexes

    @classmethod
    def ignore_attrbute(cls, key, value):
        if key in ["id", "owner_id", "arn", "unique_id"] + [
            "instance_group",
            "cluster_state",
            "master_public_dns",
            "core_instance_count",
            "core_instance_type",
            "master_instance_type",
            "master_instance_count",
        ]:
            return True
        if key in ["master_instance_group", "core_instance_group"]:
            for one in value:
                if "id" in one:
                    del one["id"]
        return False

    @classmethod
    def included_resource_types(cls):
        """resource types for this resource and its derived resources
        """
        return ["aws_emr_cluster"]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        emr = self.session.client("emr")
        items = emr.list_clusters()["Clusters"]
        for i, one in enumerate(items):
            id_ = one["Id"]
            name_ = one["Name"]
            yield self.included_resource_types()[0], name_, id_
