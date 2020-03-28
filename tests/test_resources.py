import pytest
import tempfile
import shutil

from tfcli.resources.s3 import S3


@pytest.fixture
def test_root():
    tmpd = tempfile.mkdtemp("test")
    print("temp dir is {}".format(tmpd))
    yield tmpd
    # shutil.rmtree(tmpd)


def test_resources_s3():
    s3 = S3()
    print(list(s3.list_all()))


def test_load_tfstate(test_root):
    s3 = S3(indexes=list(range(2)))
    s3.create_tfconfig(test_root)
    s3.load_tfstate(test_root)
    # repeat import, should just skip very quickly
    s3.load_tfstate(test_root)
    # # if override is true, then it should load agian
    # s3.load_tfstate(test_root, override=True)
    s3.sync_tfstate(test_root)
