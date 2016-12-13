import sys
from maya import cmds
import logging

log = logging.getLogger(__name__)

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


def create(family, subset, use_selection=False):
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

    name = "{0}_{1}_INST".format(family, subset)
    if cmds.objExists(name):
        raise RuntimeError("Instance for family and subset "
                           "already exists: {0}".format(name))

    instance = cmds.sets(name=name, empty=not use_selection)

    attrs = self.defaults + item.get("attributes", [])
    for attr in attrs:
        key = attr["key"]
        value = attr["value"](family, subset)

        if isinstance(value, bool):
            add_type = {"attributeType": "bool"}
            set_type = {"keyable": False, "channelBox": True}
        elif isinstance(value, basestring):
            add_type = {"dataType": "string"}
            set_type = {"type": "string"}
        elif isinstance(value, int):
            add_type = {"attributeType": "long"}
            set_type = {"keyable": False, "channelBox": True}
        elif isinstance(value, float):
            add_type = {"attributeType": "double"}
            set_type = {"keyable": False, "channelBox": True}
        else:
            raise TypeError("Unsupported type: %r (key: %s)" % (type(value), key))

        cmds.addAttr(instance, ln=key, **add_type)
        cmds.setAttr(instance + "." + key, value, **set_type)

    # Post creation callback
    callback = item.get("callback", None)
    if callback:
        callback(instance)

    cmds.select(instance, noExpand=True)

    return instance


def ls(family=None):
    """List instances in the scene

    Args:
        family (tuple): Tuple of family strings to filter to.
            When str is passed it will be considered as one entry in a tuple.

    Returns:
        list: Instances in the scene.

    """

    if isinstance(family, basestring):
        family = (family,)

    objsets = cmds.ls("*_INST", exactType="objectSet")

    # Only those sets that have a .family attribute
    objsets = [o for o in objsets if cmds.attributeQuery("family",
                                                         node=o,
                                                         exists=True)]

    attrs = ["family", "subset", "name", "label", "publish"]

    instances = list()
    for objset in objsets:

        instance = {
            "node": objset
        }

        # collect attributes
        for attr in attrs:
            plug = "{0}.{1}".format(objset, attr)
            if cmds.attributeQuery(attr, node=objset, exists=True):
                instance[attr] = cmds.getAttr(plug)
            else:
                log.warning("Missing attribute: %s", plug)

        if family is not None and instance['family'] not in family:
            continue

        instances.append(instance)

    return instances
