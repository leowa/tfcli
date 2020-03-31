from tfcli.resources.base import do_hcl_body, Attribute


def test_do_hcl_body_bool_attribute_value():
    a = Attribute("versioning", [dict(enabled=False, mfa_delete=False)])
    assert do_hcl_body(a) == """    versioning {
        enabled = false
        mfa_delete = false
    }"""


def test_do_hcl_body_list_of_dict():
    a = Attribute("cycle", [dict(at=10, repeat=5), dict(at=1, repeat=1000)])
    assert do_hcl_body(a) == """    cycle {
        at = 10
        repeat = 5
    }
    cycle {
        at = 1
        repeat = 1000
    }"""


def test_do_hcl_body_empty_attribute_value():
    a = Attribute(
        "website", [dict(name='', index="index.html")])
    assert do_hcl_body(a) == """    website {
        index = "index.html"
    }"""


def test_do_hcl_body_empty_list_attribute_value():
    a = Attribute(
        "website", [dict(name='', index="index.html", ref=[])])
    assert do_hcl_body(a) == """    website {
        index = "index.html"
    }"""


def test_do_hcl_body_dict_value():
    a = Attribute("tags", {
        "ingress.k8s.aws/cluster": "mpp",
        "ingress.k8s.aws/resource": "LoadBalancer",
        "kubernetes.io/namespace": "mongoproxy"
    })
    assert do_hcl_body(a) == """    tags = {
        "ingress.k8s.aws/cluster" = "mpp"
        "ingress.k8s.aws/resource" = "LoadBalancer"
        "kubernetes.io/namespace" = "mongoproxy"
    }"""


def test_do_hcl_body_dict_value_empty():
    a = Attribute("tags", {
        "ingress.k8s.aws/cluster": "",
        "ingress.k8s.aws/resource": "",
        "kubernetes.io/namespace": None
    })
    assert do_hcl_body(a) == ""
