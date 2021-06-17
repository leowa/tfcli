from .base import BaseResource
import jmespath
from ..filters import normalize_identity, arn_lastpart


class Elb(BaseResource):
    """elb resource to generate from current region"""

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
        """resource types for this resource and its derived resources"""
        return [
            "aws_alb",
            "aws_alb_listener",
            "aws_alb_listener_certificate",
            "aws_alb_listener_rule",
            "aws_alb_target_group",
            # "aws_alb_target_group_attachment",
            "aws_elb",
        ]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        elb = self.session.client("elbv2")
        for name, arn in jmespath.search(
            "LoadBalancers[*].[LoadBalancerName,LoadBalancerArn]",
            elb.describe_load_balancers(),
        ):
            yield "aws_alb", name, arn
            for larn, port, proto in jmespath.search(
                "Listeners[*].[ListenerArn,Port,Protocol]",
                elb.describe_listeners(LoadBalancerArn=arn),
            ):
                yield "aws_alb_listener", "{}-{}-{}".format(name, proto, port), larn
                if proto == "HTTPS":
                    for cert in jmespath.search(
                        "Certificates[*].CertificateArn",
                        elb.describe_listener_certificates(ListenerArn=larn),
                    ):
                        yield (
                            "aws_lb_listener_certificate",
                            normalize_identity(
                                "{}_{}".format(name, arn_lastpart(cert)),
                            ),
                            "{}_{}".format(larn, cert),
                        )
                for rarn in jmespath.search(
                    "Rules[*].RuleArn", elb.describe_rules(ListenerArn=larn)
                ):
                    yield (
                        "aws_lb_listener_rule",
                        "{}-{}-{}_{}".format(name, proto, port, arn_lastpart(rarn)),
                        rarn,
                    )

            for tarn, tname in jmespath.search(
                "TargetGroups[*].[TargetGroupArn,TargetGroupName]",
                elb.describe_target_groups(LoadBalancerArn=arn),
            ):
                yield "aws_lb_target_group", "{}_{}".format(name, tname), tarn
