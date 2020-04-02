import json
import re
from json import JSONDecodeError
from collections import namedtuple


Attribute = namedtuple('Attribute', 'name value')


def do_hcl_body(attr, tab=1):

    def process_dict(key, value, tab, pure_dict=False):
        """ pure_dict means value is a pure dict like tags, not those inside a list
        """
        if not value:  # empty dict
            return ""
        nested = [do_hcl_body(Attribute(k, v), tab + 1)
                  for k, v in value.items() if not_empty(v)]
        if not nested:
            return ""
        else:
            tabs = ' ' * 4 * tab
            return "{}{} {}{{\n".format(tabs, key, "= " if pure_dict else "") + \
                '\n'.join(nested) + "\n{}}}".format(tabs)

    key, value = attr.name, attr.value
    # TC: test_do_hcl_body_dict_value
    if not key.isidentifier():
        key = '"{}"'.format(key)
    tabs = ' ' * 4 * tab
    if isinstance(value, bool):
        return "{}{} = {}".format(tabs, key, "true" if value else "false")
    elif isinstance(value, list):
        if len(value) == 0:
            return "{}{} = []".format(tabs, key)
        if isinstance(value[0], dict):
            blocks = [process_dict(key, _, tab) for _ in value]
            blocks = [_ for _ in blocks if _]  # drop empty string
            if not blocks:
                return ""
            else:
                return "\n".join(blocks)
        else:  # plain list value
            return "{}{} = [{}]".format(tabs, key, ", ".join(['"{}"'.format(_) for _ in value]))
    elif is_json(value):
        return "{}{} = <<{}\n".format(tabs, key, key.upper()) + \
            json.dumps(json.loads(escape_interpolation(value)),
                       indent=2) + "\n{}".format(key.upper())
    elif isinstance(value, dict):
        return process_dict(key, value, tab, pure_dict=True)
    elif isinstance(value, str):
        return '{}{} = "{}"'.format(tabs, key, value) if value else ""
    else:  # other primitive types
        # this assert is very useful for us to catch something else
        assert isinstance(value, (int, float))
        return '{}{} = {}'.format(tabs, key, value)


def normalize_identity(name: str):
    return re.sub(r"[^\w]", "-", name)


def escape_interpolation(text: str):
    return re.sub(r"\$\{", "$${", text)


def is_json(text: str):
    if not isinstance(text, str):
        return False
    if "{" not in text:
        return False
    try:
        json.loads(text)
        return True
    except JSONDecodeError:
        return False


def not_empty(v):
    if isinstance(v, list):
        return len(v) != 0
    return v not in (None, '')
