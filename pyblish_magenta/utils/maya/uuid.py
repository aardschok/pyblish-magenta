from __future__ import absolute_import

import sys
import uuid

from maya import OpenMaya as om
from maya import cmds


self = sys.modules[__name__]
self._id = None


def set_uuid(node):
    """Add uuid to `node`

    Unless one already exists.

    """

    attr = "{0}.uuid".format(node)

    if not cmds.objExists(attr):
        cmds.addAttr(node, longName="uuid", dataType="string")
        cmds.setAttr(attr, str(uuid.uuid4()), type="string")
        # cmds.setAttr(attr, lock=True)


def callback(clientData):
    nodes = (set(cmds.ls(long=True)) -
             set(cmds.ls(long=True, readOnly=True)) -
             set(cmds.ls(long=True, lockedNodes=True)))

    # Add unique identifiers
    for node in nodes:
        set_uuid(node)


def register_callback():
    if self._id:
        try:
            om.MMessage.removeCallback(self._id)
            self._id = None
        except RuntimeError, e:
            print e

    self._id = om.MSceneMessage.addCallback(
        om.MSceneMessage.kBeforeSave, callback)
    print("pyblish_magenta: Registered callback")
