import pyblish.api
import pyblish_magenta.api
from maya import cmds
from pyblish_magenta.action import SelectInvalidAction


class ValidateNoUnknownNodes(pyblish.api.InstancePlugin):
    """Checks to see if there are any unknown nodes in the instance.

    This often happens if nodes from plug-ins are used but are not available
    on this machine.

    Note: Some studios use unknown nodes to store data on (as attributes)
        because it's a lightweight node.

    """

    order = pyblish_magenta.api.ValidateContentsOrder
    families = ['model', 'layout', 'rig']
    hosts = ['maya']
    optional = True
    label = "Unknown Nodes"
    actions = [SelectInvalidAction]

    @staticmethod
    def get_invalid(instance):
        return cmds.ls(instance, type='unknown')

    def process(self, instance):
        """Process all the nodes in the instance"""

        invalid = self.get_invalid(instance)
        if invalid:
            raise ValueError("Unknown nodes found: {0}".format(invalid))
