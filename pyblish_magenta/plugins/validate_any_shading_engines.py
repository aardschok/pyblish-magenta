import pyblish.api
from maya import cmds


class ValidateNoDefaultShader(pyblish.api.Validator):
    """ Ensure there's at least one shader to export """
    families = ['lookdev']
    hosts = ['maya']
    optional = True
    version = (0, 1, 0)

    def process(self, instance):
        """Process all the nodes in the instance """
        if not instance or not cmds.ls(instance, type='shadingEngine'):
            raise ValueError("No shadingEngines found to export in: {0}".format(list(instance)))