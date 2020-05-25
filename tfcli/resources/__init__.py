from collections import OrderedDict
from .base import BaseResource
from .s3 import S3
from .network import Elb, Igw, Vpc, Eip, Nif, Nacl, Rt, Sg, Subnet
from .asg import Asg, LaunchTemplate
from .elasticache import Ecc
from .iam import Iamg
from .cloudwatch import Cwa
from .sns import Sns
from .rds import Rds
from .sqs import Sqs
from .ec2 import Ec2

RESOURCE_TYPES = OrderedDict(
    {
        "elb": Elb,
        "igw": Igw,
        "vpc": Vpc,
        "eip": Eip,
        "nif": Nif,
        "nacl": Nacl,
        "rt": Rt,
        "sg": Sg,
        "subnet": Subnet,
        "asg": [Asg, LaunchTemplate],
        "ecc": Ecc,
        "ec2": Ec2,
        "rds": Rds,
        "cwa": Cwa,
        "sns": Sns,
        "sqs": Sqs,
        "iam": Iamg,
        "s3": S3,
        "network": [Elb, Igw, Vpc, Eip, Nif, Nacl, Rt, Sg, Subnet],
        "instance": [Asg, Ecc, Rds, Ec2],
    }
)

# TODO: Provide implementations for those resources
# aws_vpn_gateway: Virtual Private Gateway
# aws_kms_alias: Customer managed keys
# aws_kms_key
# aws_elb: TODO should migrate all existing to alb

# IAM resources
# aws_iam_group_membership
# aws_iam_instance_profile
# aws_iam_policy
# aws_iam_policy_attachment
# aws_iam_role
# aws_iam_role_policy
# aws_iam_user
# aws_iam_user_policy


# reference: https://github.com/dtan4/terraforming/tree/c1d467becef5645e14ff822860f3fc2a9868c066/lib/terraforming/resource
