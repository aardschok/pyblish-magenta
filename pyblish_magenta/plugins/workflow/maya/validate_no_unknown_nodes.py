import pyblish.api
from maya import cmds


class ValidateNoUnknownNodes(pyblish.api.InstancePlugin):
    """Checks to see if there are any unknown nodes in the instance.

    This often happens if nodes from plug-ins are used but are not available
    on this machine.

    Note: Some studios use unknown nodes to store data on (as attributes)
        because it's a lightweight node.

    """

    order = pyblish.api.ValidatorOrder
    families = ['model', 'layout', 'rig']
    hosts = ['maya']
    category = 'cleanup'
    optional = True
    version = (0, 1, 0)
    label = "Unknown Nodes"

    def process(self, instance):
        """Process all the nodes in the instance"""
        unknown_nodes = cmds.ls(instance, type='unknown')
        if unknown_nodes:
            raise ValueError("Unkown nodes found: {0}".format(unknown_nodes))
