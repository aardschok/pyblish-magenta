import pyblish.api
import pyblish_magenta.api
from pyblish_magenta.action import (
    SelectInvalidAction,
    RepairAction
)

from maya import cmds


class ValidateNoIntermediateObjects(pyblish.api.InstancePlugin):
    """Ensure no intermediate objects are in the Instance"""

    order = pyblish_magenta.api.ValidateContentsOrder
    families = ['model']
    hosts = ['maya']
    label = "No Intermediate Objects"
    actions = [SelectInvalidAction, RepairAction]

    @staticmethod
    def get_invalid(instance):

        intermediates = cmds.ls(instance,
                                shapes=True,
                                intermediateObjects=True,
                                long=True)
        return intermediates

    def process(self, instance):
        """Process all the intermediateObject nodes in the instance"""
        intermediate_objects = cmds.ls(instance,
                                       shapes=True,
                                       intermediateObjects=True,
                                       long=True)
        if intermediate_objects:
            raise ValueError("Intermediate objects found: "
                             "{0}".format(intermediate_objects))

    @staticmethod
    def repair(instance):
        """Delete all intermediateObjects"""

        invalid = ValidateNoIntermediateObjects.get_invalid(instance)
        if invalid:
            future = cmds.listHistory(invalid, future=True)
            cmds.delete(future, ch=True)
            cmds.delete(invalid)
