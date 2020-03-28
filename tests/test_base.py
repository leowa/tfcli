from tfcli.resources.base import do_hcl_body, Attribute


def test_do_hcl_body_bool_attribute_value():
    a = Attribute("versioning", [dict(enabled=False, mfa_delete=False)])
    assert do_hcl_body(a) == """    versioning {
        enabled = false
        mfa_delete = false
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
