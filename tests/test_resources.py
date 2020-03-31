import pytest
import tempfile
import shutil

from tfcli.resources import BaseResource
from tfcli.resources import S3, Elb, Igw, Asg


@pytest.fixture
def test_root():
    tmpd = tempfile.mkdtemp("test")
    print("temp dir is {}".format(tmpd))
    yield tmpd
    # shutil.rmtree(tmpd)


def _test_load_and_validate(res: BaseResource, root, should_no_diff=True):
    print(list(res.list_all()))
    res.create_tfconfig(root)
    res.load_tfstate(root)
    res.sync_tfstate(root)
    assert res.show_plan_diff(root) in (0) if should_no_diff else (0, 1)


def test_load_tfstate_s3(test_root):
    # TODO: need to execute plan for s3 to apply additional default values
    _test_load_and_validate(S3(indexes=list(range(10))),
                            root=test_root, should_no_diff=False)


def test_load_tfstate_elb(test_root):
    _test_load_and_validate(Elb(), test_root)


def test_load_tfstate_igw(test_root):
    _test_load_and_validate(Igw(), test_root)


def test_load_tfstate_asg(test_root):
    # TODO: apply change to for more default values
    _test_load_and_validate(Asg(), root=test_root, should_no_diff=False)
