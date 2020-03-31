import pytest
import tempfile
import shutil

from tfcli.resources.s3 import S3
from tfcli.resources.elb import Elb


@pytest.fixture
def test_root():
    tmpd = tempfile.mkdtemp("test")
    print("temp dir is {}".format(tmpd))
    yield tmpd
    shutil.rmtree(tmpd)


def test_resources_s3():
    s3 = S3()
    print(list(s3.list_all()))


def test_load_tfstate_s3(test_root):
    res = S3(indexes=list(range(2)))
    res.create_tfconfig(test_root)
    res.load_tfstate(test_root)
    # repeat import, should just skip very quickly
    res.load_tfstate(test_root)
    # # if override is true, then it should load agian
    # res.load_tfstate(test_root, override=True)
    res.sync_tfstate(test_root)


def test_resources_elb():
    elb = Elb()
    print(list(elb.list_all()))


def test_load_tfstate_elb(test_root):
    test_root = "/var/folders/2v/jmznxpkx54q_hc7r27nx2q0c0000gp/T/tmp6g2w6_qntest"
    res = Elb()
    res.create_tfconfig(test_root)
    res.load_tfstate(test_root)
    res.sync_tfstate(test_root)
