from .base import BaseResource


class Asg(BaseResource):
    """ autoscaling group resource to generate from current region
    """
    def __init__(self, logger=None):
        super().__init__(logger)

    def amend_attributes(self, _type, _name, attributes: dict):
        if "launch_template" in attributes and attributes["launch_template"]:
            tpl = attributes["launch_template"][0]
            if "id" in tpl and "name" in tpl:  # remove name from template if id exists
                del tpl["name"]
        return attributes

    @classmethod
    def ignore_attrbute(cls, key, value):
        if key in ["id", "owner_id", "arn"]:
            return True
        return False

    @classmethod
    def included_resource_types(cls):
        """resource types for this resource and its derived resources
        """
        return [
            "aws_autoscaling_group",
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        asg = self.session.client("autoscaling")
        items = asg.describe_auto_scaling_groups()["AutoScalingGroups"]
        for item in items:
            _name = _id = item["AutoScalingGroupName"]
            yield "aws_autoscaling_group", _name, _id
