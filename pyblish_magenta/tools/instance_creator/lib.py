import sys
from maya import cmds

self = sys.modules[__name__]
self.defaults = []
self.families = []


def register_default(item):
    """Register new default attribute

    Dictionary structure:
    {
        "key": "Name of attribute",
        "value": "Value of attribute",
        "help": "Documentation"
    }

    Arguments:
        default (dict): New default Attribute

    """

    assert "key" in item
    assert "value" in item

    self.defaults.append(item)


def register_family(item):
    """Register family and attributes for family

    Dictionary structure:
    {
        "name": "Name of attribute",
        "help": "Documentation",
        "subsets": ["list", "of" "subsets"],
        "attributes": [
            {
                "...": "Same as default",
            }
        ]
    }

    Arguments:
        default (dict): New family

    """

    assert "name" in item

    # If family was already registered then overwrite it
    for i, family in enumerate(self.families):
        if item['name'] == family['name']:
            self.families[i] = item
            return

    self.families.append(item)


def create(family, subset=None, use_selection=False):
    """Create new instance

    Arguments:
        family (str): Name of family, prefixed with subset
        subset (str): Name of subset
        use_selection (bool): Use selection to create this instance?

    """

    try:
        item = next(i for i in self.families if i["name"] == family)
    except:
        raise RuntimeError("{0} is not a valid family".format(family))

    attrs = self.defaults + item.get("attributes", [])

    if not use_selection:
        cmds.select(deselect=True)

    instance = cmds.sets(name="{0}_{1}_INST".format(family, subset))

    for item in attrs:
        key = item["key"]
        value = item["value"](family, subset)

        if isinstance(value, bool):
            add_type = {"attributeType": "bool"}
            set_type = {"keyable": False, "channelBox": True}
        elif isinstance(value, basestring):
            add_type = {"dataType": "string"}
            set_type = {"type": "string"}
        elif isinstance(value, int):
            add_type = {"attributeType": "long"}
            set_type = {"keyable": False, "channelBox": True}
        else:
            raise TypeError("Unsupported type: %r" % type(value))

        cmds.addAttr(instance, ln=key, **add_type)
        cmds.setAttr(instance + "." + key, value, **set_type)

    cmds.select(instance, noExpand=True)

    return instance
