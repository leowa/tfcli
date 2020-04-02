from .base import BaseResource
from ..filters import normalize_identity


class Cwa(BaseResource):
    """ Cloud watch alert resource to generate from current region
    """

    def __init__(self, logger=None):
        super().__init__(logger)

    @classmethod
    def ignore_attrbute(cls, key, value):
        if key in ["id", "owner_id", "arn"]:
            return True
        if key == "datapoints_to_alarm" and value == 0:
            return True
        return False

    @classmethod
    def included_resource_types(cls):
        """resource types for this resource and its derived resources
        """
        return ["aws_cloudwatch_metric_alarm"]

    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """
        cw = self.session.client("cloudwatch")
        alarms = cw.describe_alarms()["MetricAlarms"]
        for one in alarms:
            name = one["AlarmName"]
            yield "aws_cloudwatch_metric_alarm", normalize_identity(name), name
