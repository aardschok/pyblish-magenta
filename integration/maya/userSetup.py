from __future__ import absolute_import

import os
import maya.mel
import maya.cmds
import maya.utils

from PySide.QtGui import QApplication

try:
    import pyblish_magenta.api
    pyblish_magenta.api.setup()

    import pyblish_magenta.utils.maya.uuid
    pyblish_magenta.utils.maya.uuid.register_callback()

    import pyblish_magenta.utils.maya.lib
    maya.utils.executeDeferred(
        pyblish_magenta.utils.maya.lib.create_menu)

except ImportError as e:
    print("pyblish_magenta: Could not load Magenta: %s" % e)


def set_project():
    """The current working directory is assumed to be the Maya Project"""
    maya_dir = os.path.join(os.getcwd(), "maya")

    if not os.path.exists(maya_dir):
        os.makedirs(os.path.join(maya_dir, "scenes"))

    if os.name == "nt":
        # MEL can't handle backslash
        maya_dir = maya_dir.replace("\\", "/")

    print("Setting development directory to: %s" % maya_dir)
    maya.mel.eval('setProject \"' + maya_dir + '\"')


def distinguish():
    """Distinguish GUI from other projects

    This adds a green line to the top of Maya's GUI

    """

    QApplication.instance().setStyleSheet("""
    QMainWindow > QMenuBar {
      border-bottom: 1px solid lightgreen;
    }
    """)


def setup_lighting():
    """Initialise Maya scene for lighting

    NOTE(marcus): This should be made more formal, such as a dedicated
    click to open a GUI allowing an artist to initialise his scene for
    the task at hand, such as lighting but also animation and
    compositing, regardless of host.

    """

    print("Setting up for lighting..")
    attrs = {
        "imageFormat": {
            "value": 32
        },
        "imageFilePrefix": {
            "value": "<Scene>/<Layer>/defaultpass/<Layer>_defaultpass",
            "type": "string",
        }
    }

    for key, data in attrs.iteritems():
        value = data["value"]
        kwargs = {}
        if "type" in data:
            kwargs["type"] = data["type"]

        print("%s = %s" % (key, value))
        maya.cmds.setAttr("defaultRenderGlobals.%s" % key, value, **kwargs)


set_project()
maya.utils.executeDeferred(distinguish)

if os.environ.get("TOPICS", "").split()[-1] == "lighting":
    maya.utils.executeDeferred(setup_lighting)
