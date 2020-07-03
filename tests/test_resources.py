import shutil
import tempfile

import pytest

from tfcli.resources import (
    S3,
    Asg,
    LaunchTemplate,
    BaseResource,
    Cwa,
    Ecc,
    Eip,
    Elb,
    Iamg,
    InstanceProfile,
    Igw,
    Vpc,
    Nif,
    Nacl,
    Rt,
    Sg,
    Subnet,
    Sns,
    Rds,
    Sqs,
    Ec2,
    Emr,
)


@pytest.fixture
def test_root():
    tmpd = tempfile.mkdtemp("test")
    print("temp dir is {}".format(tmpd))
    yield tmpd
    shutil.rmtree(tmpd)


def _test_load_and_validate(res: BaseResource, root, should_no_diff=True):
    print(list(res.list_all()))
    res.create_tfconfig(root)
    res.load_tfstate(root)
    res.sync_tfstate(root)
    assert res.show_plan_diff(root) in (0,) if should_no_diff else (0, 1)


def test_load_tfstate_s3(test_root):
    # TODO: need to execute plan for s3 to apply additional default values
    _test_load_and_validate(
        S3(indexes=list(range(10))), root=test_root, should_no_diff=False
    )


def test_load_tfstate_elb(test_root):
    _test_load_and_validate(Elb(), test_root)


def test_load_tfstate_igw(test_root):
    _test_load_and_validate(Igw(), test_root)


def test_load_tfstate_asg(test_root):
    # TODO: apply change to for more default values
    _test_load_and_validate(Asg(), root=test_root, should_no_diff=False)


def test_load_tfstate_vpc(test_root):
    _test_load_and_validate(Vpc(), test_root)


def test_load_tfstate_eip(test_root):
    _test_load_and_validate(Eip(indexes=list(range(5))), test_root)


def test_load_tfstate_ecc(test_root):
    _test_load_and_validate(Ecc(), test_root)


def test_load_tfstate_iamg(test_root):
    _test_load_and_validate(Iamg(), test_root)


def test_load_tfstate_cwa(test_root):
    # TODO: `+ treat_missing_data        = "missing"`
    _test_load_and_validate(Cwa(), test_root, should_no_diff=False)


def test_load_tfstate_nif(test_root):
    _test_load_and_validate((Nif(indexes=list(range(1)))), test_root)


def test_load_tfstate_nacl(test_root):
    _test_load_and_validate((Nacl(indexes=list(range(1)))), test_root)


def test_load_tfstate_rt(test_root):
    _test_load_and_validate((Rt()), test_root)


def test_load_tfstate_sg(test_root):
    _test_load_and_validate((Sg(indexes=list(range(3)))), test_root)


def test_load_tfstate_subnet(test_root):
    _test_load_and_validate((Subnet(indexes=list(range(3)))), test_root)


def test_load_tfstate_sns(test_root):
    _test_load_and_validate((Sns(indexes=list(range(3)))), test_root)


def test_load_tfstate_rds(test_root):
    _test_load_and_validate((Rds(indexes=list(range(3)))), test_root)


def test_load_tfstate_sqs(test_root):
    _test_load_and_validate((Sqs(indexes=list(range(3)))), test_root)


def test_load_tfstate_ec2(test_root):
    _test_load_and_validate((Ec2(indexes=list(range(5)))), test_root)


def test_load_tfstate_lt(test_root):
    _test_load_and_validate(LaunchTemplate(), test_root)


def test_load_tfstate_instance_profile(test_root):
    _test_load_and_validate(InstanceProfile(), test_root)


def test_load_tfstate_emr(test_root):
    _test_load_and_validate(Emr(), test_root)
