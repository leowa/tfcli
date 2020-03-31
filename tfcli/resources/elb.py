from .base import BaseResource


class Elb(BaseResource):
    """ elb resource to generate from current region
    """

    def __init__(self, logger=None, indexes=None):
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
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        elb = self.session.client("elbv2")
        items = elb.describe_load_balancers()["LoadBalancers"]
        for item in items:
            yield "aws_alb", item["LoadBalancerName"], item["LoadBalancerArn"]
