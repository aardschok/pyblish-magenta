from maya import cmds
from pyblish_magenta.vendor import inflection
import sys


# (key, value, help)
defaults = [
    ("publish", lambda name, family: True,
        "The active state of the instance"),
    ("name", lambda name, family: name,
        "Name of instance"),
    ("family", lambda name, family: family,
        "Which family to associate this instance with"),
    ("label", lambda name, family: inflection.titleize(name),
        "Optional label for this instance, used in GUIs"),
    ("subset", lambda name, family: "default",
        "Which subset to associate this instance with"),
    ("category", lambda name, family: "",
        "Optional category used as metadata by other tools"),
    ("tags", lambda name, family: "",
        "A space-separated series of tags to imprint with cQuery"),
]

families = {
    "model": [],
    "rig": [],
    "look": [],
    "pointcache": [],
    "animation": [],
    "threejs": [],      # Export models, shaders, textures to three.JS json format
    "vraybake": [],     # Bake textures with v-ray for objects
    "proxy": [],        # (Animated) Proxies that go to Alembic + gpuCache with objectIds
    "vrmeshReplace": []   # Replaced gpuCaches to vrmesh -> is simple .ma file
}


def create(name, family, use_selection=False):

    if not family in families:
        raise RuntimeError("{0} is not a valid family".format(family))

    if not use_selection:
        cmds.select(deselect=True)

    instance = cmds.sets(name=name + "_INST")

    for key, value, _ in defaults + families[family]:
        cmds.addAttr(instance, ln=key, **attributes[key]["add"])
        cmds.setAttr(instance + "." + key,
                     value(name, family),
                     **attributes[key]["set"])

    return instance


attributes = {
    "publish": {
        "add": {"attributeType": "bool"},
        "set": {"keyable": False, "channelBox": True}
    },
    "family": {
        "add": {"dataType": "string"},
        "set": {"type": "string"}
    },
    "category": {
        "add": {"dataType": "string"},
        "set": {"type": "string"}
    },
    "name": {
        "add": {"dataType": "string"},
        "set": {"type": "string"}
    },
    "label": {
        "add": {"dataType": "string"},
        "set": {"type": "string"}
    },
    "subset": {
        "add": {"dataType": "string"},
        "set": {"type": "string"}
    },
    "tags": {
        "add": {"dataType": "string"},
        "set": {"type": "string"}
    },
}
