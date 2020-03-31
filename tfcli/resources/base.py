import boto3
import logging
import json
import jinja2
from uuid import uuid4
from os import path
from abc import ABCMeta, abstractmethod

from ..util import run_cmd
from ..filters import do_hcl_body, Attribute


class BaseResource(metaclass=ABCMeta):
    """ S3 resource to generate from current region
    """

    def __init__(self, logger=None):
        if not logger:
            self.logger = logging.getLogger(__name__)
            logging.basicConfig(
                level=logging.INFO, format="%(asctime)-15s %(clientip)s %(user)-8s %(message)s")
        self.session = boto3.Session()

    @classmethod
    def my_jinja_env(cls):
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(path.dirname(__file__)))
        env.filters['hcl_body'] = do_hcl_body
        return env

    @classmethod
    @abstractmethod
    def ignore_attrbute(cls, key, value):
        """whether ignoring this attribute from tfstate file
        """

    @classmethod
    @abstractmethod
    def included_resource_types(cls):
        """resource types for this resource and its derived resources
           refer to: https://github.com/terraform-providers/terraform-provider-aws/blob/cb72b1f24c1344533c32f421263db84e39bdd824/aws/provider.go
        """

    @abstractmethod
    def list_all(self):
        """list all such kind of resources from AWS

        :return: list of tupe for a resource (type, name, id)
        """

    def create_tfconfig(self, root, config_file="main.tf"):
        """create a terraform configuration file skeleton for this type of resources

        :param root: root directory to put configuration file into, default to pwd
        :param config_file: config file to write/merge to
        """
        if not root:
            root = path.curdir
        if not path.isabs(config_file):
            config_file = path.join(root, config_file)
        tf_template = self.my_jinja_env().get_template("tf.j2")
        data = tf_template.render(instances=self.list_all())
        with open(config_file, "wt") as fd:
            fd.truncate()
            fd.write(data)

    def load_tfstate(self, root, state_file="terraform.tfstate", override=False):
        """import terraform state for this kind of resources

        :param root: root directory to put state file into, default to pwd
        :param state_file: state file to write/merge to
        :param override: whether to override this type of resource state
        """
        if not root:
            root = path.curdir
        if not path.isabs(state_file):
            state_file = path.join(root, state_file)

        # get list of all existing resource state with <resource_type>.<resource_name> as key
        existing = set()
        if path.exists(state_file):
            with open(state_file, 'rt') as fd:
                jdata = json.load(fd)
            kept = []
            for res in jdata['resources']:
                if not override or res['type'] not in self.included_resource_types():
                    existing.add("{}.{}".format(res["type"], res["name"]))
                    kept.append(res)
            if override:
                jdata['resources'] = kept
                with open(state_file, 'wt') as fd:
                    fd.truncate()
                    json.dump(jdata, fd, indent=2)
        else:  # create an empty `container`
            meta = dict(version=4, terraform_version="0.12.24", serial=1,
                        lineage=str(uuid4()), output=dict(), resouces=list())
            with open(state_file, 'wt') as fd:
                fd.truncate()
                json.dump(meta, fd, indent=2)

        failed = []
        for i, (_type, name, _id) in enumerate(self.list_all()):
            if i == 0:
                rc = run_cmd(["terraform", "init"], self.logger, root)
                if rc != 0:
                    exit(rc)
            # import is slow, avoid this if resource exists in state file and no need to override
            if not override and "{0}.{1}".format(_type, name) in existing:
                continue
            _id = _id or name  # use name as Id if not provided
            cmd = ["terraform", "import", "-config={}".format(root),
                   "-state-out={}".format(state_file),
                   "{0}.{1}".format(_type, name), _id]
            rc = run_cmd(cmd, self.logger, root)
            if rc != 0:
                failed.append(' '.join(cmd))
        if failed:
            self.logger.error("=" * 20 + __name__ +
                              " LOAD FAILURE" + "=" * 20)
            self.logger.error("\n".join(['', *failed]))
            self.logger.error("=" * 20 + __name__ +
                              " LOAD FAILURE" + "=" * 20)

    def sync_tfstate(self, root, tf_file="main.tf", state_file="terraform.tfstate"):
        """sync resource configuration from a state_file,
           to keep current resource sync to currently deployed state

        :param root: root directory to put tf file into, default to pwd
        :param tf_file: terraform tf file to generate
        :param state_file: terraform state file with the lastest resource state
        """
        if not root:
            root = path.curdir
        if not path.isabs(state_file):
            state_file = path.join(root, state_file)
        if not path.isabs(tf_file):
            tf_file = path.join(root, tf_file)

        with open(state_file, 'rt') as fd:
            data = json.load(fd)
            resources = data['resources']

        items = []
        for item in resources:
            _name, _type, inst = item['name'], item['type'], item['instances'][0]
            raw = inst['attributes']
            attrs = []
            for k in sorted(raw.keys()):
                # skip ignored attributes
                # ignore some Empty attributes
                # and also skip attributes that means empty
                # such as access_logs in alb with "enabled" as "false"
                v = raw[k]
                if self.ignore_attrbute(k, v) or not v:
                    continue
                attrs.append(Attribute(name=k, value=v))
            items.append((_type, _name, attrs))
        tf_template = self.my_jinja_env().get_template("tf.j2")
        data = tf_template.render(instances=items)
        with open(tf_file, 'wt') as fd:
            fd.truncate()
            fd.write(data)
        run_cmd(["terraform", "fmt", path.basename(tf_file)],
                logger=self.logger, cwd=root)
